# main.py

import streamlit as st
import mysql.connector

# Establish database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="hostname",
            user="username",
            password="password",
            database="databasename"
        )
        return connection
    except mysql.connector.Error as err:
        print("Error: ", err)
        return None

# Function to simulate user authentication
def authenticate(username, password):
    # Authenticate user from database
    return False

# Page: Home
def page_home():
    st.markdown("<h1 style='text-align: center;'>Online Learning Platform</h1>", unsafe_allow_html=True)
    st.image("front.jpg", use_column_width=True)


# Main function
def main():
    page_home()
    

if __name__ == "__main__":
    main()
