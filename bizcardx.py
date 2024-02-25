import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
import pymysql
from PIL import Image
import easyocr
from streamlit_option_menu import option_menu
import pandas as pd
import re
import numpy as np
import io
import base64

myconnect = pymysql.connect(host = '127.0.0.1', user = 'root', passwd = 'Sw@30')

cur = myconnect.cursor()
cur.execute('CREATE DATABASE if not exists bizcardx')
cur.execute('Use bizcardx')

# SETTING PAGE CONFIGURATIONS
#def new_func():
 #   image = Image.open("C:\\Users\\krkar\\OneDrive\\Documents\\background image.jpg")
  #  return image

#icon = new_func()
# Login and Logout Section
st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR",
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """# This OCR app is created by *Swathi*!"""})
import streamlit as st

# Initialize login status in session state
if 'login_status' not in st.session_state:
    st.session_state.login_status = False

st.sidebar.header(":wave: :red[**Welcome to my application!**]")
st.sidebar.subheader(":red[**🔐User Login**]")

# Check if username and password fields are empty
if not st.session_state.login_status:
    username = st.sidebar.text_input("User Name", key="username_input")
    password = st.sidebar.text_input("Password", type='password', key="password_input")

    # Prompt message if both username and password fields are empty
    if not username and not password:
        st.sidebar.write("Please enter your username and password to login.")

    # Enable login button only if both username and password are provided
    if username and password:
        login_button = st.sidebar.button("Login")
    else:
        login_button = False

    # Perform login when login button is clicked
    if login_button:
        entered_username = username
        entered_password = password
        st.session_state.login_status = True
        st.sidebar.success("Login Successful!")

# Perform logout when logout button is clicked
if st.session_state.login_status:
    logout_button = st.sidebar.button("Logout")
    if logout_button:
        st.session_state.login_status = False
        st.sidebar.success("Logout Successful!")

# Display content after successful login
if st.session_state.login_status:
    st.markdown("<h1 style='text-align: center; color: Red;'>BizCardX: Extracting Business Card Data with OCR</h1>",
                unsafe_allow_html=True)


    selected = option_menu(None, ["Home", "Upload Image", "Make Changes","Delete"],
                        icons=["house", "cloud-upload", "vector-pen","pencil-square"],
                        default_index=0,
                        orientation="horizontal",
                        styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "-2px",
                                                "--hover-color": "#545454"},
                                "icon": {"font-size": "20px"},
                                "container": {"max-width": "7000px"},
                                "nav-link-selected": {"background-color": "#ff5757"}})

    # HOME MENU
    if selected == "Home":
        col1, col2 = st.columns([2, 2],gap="medium")
        with col1:
            st.image(Image.open("C:\\Users\\krkar\\OneDrive\\Documents\\background image.jpg"), width=500)
            st.markdown("### :red[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        with col2:
            st.write(
                "### :red[**About :**] Bizcard is a Python application designed to extract information from business cards.")
            st.write(
                '### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

    # DELETE MENU
    if selected == "Delete":
        col1, col2 = st.columns([4, 4])
        with col1:
            cur.execute("SELECT NAME FROM BUSINESS_CARD")
            Y = cur.fetchall()
            names = []
            for i in Y:
                names.append(i[0])
            name_selected = st.selectbox("Select the name to delete", options=names)
            # st.write(name_selected)
        
        
        with col2:
            st.write(" ")
            st.write(" ")
            remove = st.button("Clik here to delete")
        if name_selected and remove:
            cur.execute(
                f"DELETE FROM BUSINESS_CARD WHERE NAME = '{name_selected}'")
            myconnect.commit()
            if remove:
                st.warning('DELETED', icon="⚠️")

    # extract the data
    def extracted_text(picture):
        ext_dic = {'Name': [], 'Designation': [], 'Company_name': [], 'Contact': [], 'Email': [], 'Website': [],
                'Area': [], 'State': [], 'City': [], 'Pincode': []}

        ext_dic['Name'].append(result[0])
        ext_dic['Designation'].append(result[1])
        
        for m in range(2, len(result)):
            if result[m].startswith('+') or (result[m].replace('-', '').isdigit() and '-' in result[m]):
                ext_dic['Contact'].append(result[m])

            elif '@' in result[m] and '.com' in result[m]:
                small = result[m].lower()
                ext_dic['Email'].append(small)

            elif 'www' in result[m] or 'WWW' in result[m] or 'wwW' in result[m] and '.com' in result[m]:
                small = result[m].lower()
                ext_dic['Website'].append(small)

            
            # To get AREA
            elif re.findall(r'^[0-9].+, [a-zA-Z]+', result[m]):
                ext_dic["Area"].append(result[m].split(',')[0])
            elif re.findall(r'[0-9] [a-zA-Z]+', result[m]):
                ext_dic["Area"].append(result[m])
            
            # To get CITY NAME
            match1 = re.findall('.+St , ([a-zA-Z]+).+', result[m])
            match2 = re.findall('.+St,, ([a-zA-Z]+).+', result[m])
            match3 = re.findall('^[E].*', result[m])
            if match1:
                ext_dic["City"].append(match1[0])
            elif match2:
                ext_dic["City"].append(match2[0])
            elif match3:
                ext_dic["City"].append(match3[0])
                
            # To get STATE
            state_match = re.findall(r'[a-zA-Z]{9} +[0-9]', result[m])
            if state_match:
                ext_dic["State"].append(result[m][:9])
            elif re.findall(r'^[0-9].+, ([a-zA-Z]+);', result[m]):
                ext_dic["State"].append(result[m].split()[-1])
            if len(ext_dic["State"]) == 2:
                ext_dic["State"].pop(0)

            # To get PINCODE
            if len(result[m]) >= 7 and result[m].isdigit():
                ext_dic["Pincode"].append(result[m])
            elif re.findall(r'[a-zA-Z]{9} +[0-9]', result[m]):
                ext_dic["Pincode"].append(result[m][10:])

            
            elif re.findall(r'^[A-Za-z]', result[m]):
                # Extract only the company name part excluding email id and website
                company_name = re.split(r'(?:\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b|www|WWW|wwW|\.[a-zA-Z]+\.com)', result[m])[0]
                ext_dic['Company_name'].append(company_name.strip())

            elif re.findall(r'^[A-Za-z]', result[m]):
                # Extract only the company name part excluding email id and website
                company_name = re.split(r'(?:www|WWW|wwW|\.[a-zA-Z]+\.com|[a-zA-Z]+, [a-zA-Z]+)', result[m])[0]
                ext_dic['Company_name'].append(company_name.strip())
                
        for key, value in ext_dic.items():
            if len(value) > 0:
                concatenated_string = ' '.join(value)
                ext_dic[key] = [concatenated_string]
            else:
                value = 'NA'
                ext_dic[key] = [value]
        
        return ext_dic


    if selected == "Upload Image":
        image = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")


        @st.cache_data
        def load_image():
            reader = easyocr.Reader(['en'], model_storage_directory=".")
            return reader

        reader_1 = load_image()
        if image is not None:
            input_image = Image.open(image)
            # Setting Image size
            st.markdown(
            "<div style='text-align: center;'>"
            "<img src='data:image/png;base64," + 
            base64.b64encode(image.getvalue()).decode() + 
            "' style='width: 600px;'>"
            "</div>",
            unsafe_allow_html=True)

            result = reader_1.readtext(np.array(input_image), detail=0)

            # creating dataframe
            ext_text = extracted_text(result)
            df = pd.DataFrame(ext_text)
            st.dataframe(df)
            # Converting image into bytes
            image_bytes = io.BytesIO()
            input_image.save(image_bytes, format='PNG')
            image_data = image_bytes.getvalue()
            # Creating dictionary
            data = {"Image": [image_data]}
            df_1 = pd.DataFrame(data)
            concat_df = pd.concat([df, df_1], axis=1)

            # Database
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                selected = option_menu(
                    menu_title=None,
                    options=["Preview"],
                    icons=['file-earmark'],
                    default_index=0,
                    orientation="horizontal")

                ext_text = extracted_text(result)
                df = pd.DataFrame(ext_text)
            if selected == "Preview":
                col_1, col_2 = st.columns([4, 4])
                with col_1:
                    modified_n = st.text_input('Name', ext_text["Name"][0])
                    modified_d = st.text_input('Designation', ext_text["Designation"][0])
                    modified_c = st.text_input('Company_name', ext_text["Company_name"][0])
                    modified_con = st.text_input('Mobile', ext_text["Contact"][0])
                    modified_m = st.text_input('Email', ext_text["Email"][0])
                    concat_df["Name"] = modified_n
                    concat_df["Designation"] = modified_d
                    concat_df["Company_name"] = modified_c
                    concat_df["Contact"] = modified_con
                    concat_df["Email"] = modified_m
                with col_2:
                    modified_w = st.text_input('Website', ext_text["Website"][0])
                    modified_a = st.text_input('Area', ext_text["Area"][0])
                    modified_ci = st.text_input('City', ext_text["City"][0])
                    modified_s = st.text_input('State',ext_text['State'][0])
                    modified_p = st.text_input('Pincode', ext_text["Pincode"][0])
                    concat_df["Website"] = modified_w
                    concat_df["Area"] = modified_a
                    concat_df["City"] = modified_ci
                    concat_df["State"] = modified_s
                    concat_df["Pincode"] = modified_p

                col3, col4 = st.columns([4, 4])
                with col3:
                    Preview = st.button("Preview modified text")
                with col4:
                    Upload = st.button("Upload to Database")
                if Preview:
                    filtered_df = concat_df[
                        ['Name', 'Designation', 'Company_name', 'Contact', 'Email', 'Website', 'Area', 'City', 'State', 'Pincode']]
                    st.dataframe(filtered_df)
                else:
                    pass

                if Upload:
                    with st.spinner("In progress"):
                        cur.execute(
                            "CREATE TABLE IF NOT EXISTS BUSINESS_CARD(NAME VARCHAR(50), DESIGNATION VARCHAR(100), " \
                            "COMPANY_NAME VARCHAR(100), CONTACT VARCHAR(35), EMAIL VARCHAR(100), WEBSITE VARCHAR(100), " \
                            "AREA TEXT, CITY TEXT, STATE TEXT, PINCODE VARCHAR(100))"
                        )

                        myconnect.commit()
                        A = "INSERT INTO BUSINESS_CARD(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL, WEBSITE, AREA, " \
                            "CITY, STATE, PINCODE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        for index, i in concat_df.iterrows():
                            result_table = (i["Name"], i["Designation"], i["Company_name"], i["Contact"], i["Email"], i["Website"], i["Area"], i["City"], i["State"], i["Pincode"])
                            cur.execute(A, result_table)
                            myconnect.commit()
                            st.success('SUCCESSFULLY UPLOADED', icon="✅")
        else:
            st.write("Upload an image")
    
    if selected == "Make Changes":
        st.markdown(":black[Alter the data here]")
        try:
                cur.execute("SELECT Name FROM business_card")
                result = cur.fetchall()
                business_cards = {}
                for row in result:
                    business_cards[row[0]] = row[0]
                options = ["Select Card"] + list(business_cards.keys())
                selected_card = st.selectbox("**Select a card**", options)
                if selected_card == "Select Card":
                    st.write("Card not selected")
                else:
                    st.markdown("#### Update or modify the data below")
                    cur.execute('''Select Name,Designation,Company_Name,
                    Contact,Email,Website,Area,City,State,Pincode from business_card WHERE Name=%s''',
                    (selected_card,))
                    result = cur.fetchone()

                    # DISPLAYING ALL THE INFORMATIONS
                    col1, col2 = st.columns([4, 4])
                    with col1:
                        company_name = st.text_input("Company_Name", result[2])
                        card_holder = st.text_input("Name", result[0])
                        designation = st.text_input("Designation", result[1])
                        mobile_number = st.text_input("Contact", result[3])
                        email = st.text_input("Email", result[4])
                    with col2:    
                        website = st.text_input("Website", result[5])
                        area = st.text_input("Area", result[6])
                        city = st.text_input("City", result[7])
                        state = st.text_input("State", result[8])
                        pin_code = st.text_input("Pincode", result[9])



                    if st.button(":black[Commit changes to DB]"):
                        
                        # Update the information for the selected business card in the database
                        cur.execute("""UPDATE business_card SET Name=%s,Designation=%s,Company_Name=%s,Contact=%s,Email=%s,Website=%s,
                                        Area=%s,City=%s,State=%s,Pincode=%s where Name=%s""",
                                        (card_holder,designation,company_name, mobile_number, email, website, area, city, state, pin_code,
                        selected_card))

                        myconnect.commit()
                        st.success("Information updated in database successfully.")

                if st.button(":black[View data]"):
                    cur.execute('''Select Name,Designation,Company_Name,
                    Contact,Email,Website,Area,City,State,Pincode from business_card''')
                    updated_df2 = pd.DataFrame(cur.fetchall(),
                                            columns=["Name","Designation","Company_Name",
                    "Contact","Email","Website","Area","City","State","Pincode"])
                    st.write(updated_df2)
        except:
                    st.warning("There is no data available in the database")
                