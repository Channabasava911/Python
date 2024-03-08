import streamlit as st
import mysql.connector

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

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
        st.error("Error: {}".format(err))
        return None


# Login page
def login_page():
    st.title("Admin Panel - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")
    
    if login_button:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM admins WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            admin = cursor.fetchone()
            if admin:
                st.session_state['logged_in'] = True
                st.success("Login Successful!")
            else:
                st.error("Invalid username or password. Please try again.")
            cursor.close()
            connection.close()

# Function to view existing courses
def view_courses_page():
    st.title("View Courses")
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM courses"
        cursor.execute(query)
        courses = cursor.fetchall()
        if courses:
            st.write("Available Courses:")
            for course in courses:
                st.write(f"Course ID: {course['course_id']}, Course Name: {course['course_name']}, Duration: {course['duration']}, Fee: {course['fee']}")
        else:
            st.write("No courses available.")
        cursor.close()
        connection.close()

# Function to create a course
def create_course_page():
    st.title("Create Course")
    name = st.text_input("Enter Course Name")
    duration = st.text_input("Enter Course Duration")
    fee = st.text_input("Enter Course Fee")
    create_button = st.button("Create Course")

    if create_button and name and duration and fee:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "INSERT INTO courses (course_name, duration, fee) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, duration, fee))
            connection.commit()
            st.success("Course created successfully!")
            cursor.close()
            connection.close()
        else:
            st.error("Error connecting to the database.")

# Function to delete a course
def delete_course_page():
    st.title("Delete Course")
    course_id = st.text_input("Enter Course ID")
    delete_button = st.button("Delete Course")

    if delete_button and course_id:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "DELETE FROM courses WHERE course_id = %s"
            cursor.execute(query, (course_id,))
            connection.commit()
            st.success("Course deleted successfully!")
            cursor.close()
            connection.close()
        else:
            st.error("Error connecting to the database.")

# Function to update a course
def update_course_page():
    st.title("Update Course")
    course_id = st.text_input("Enter Course ID")
    name = st.text_input("Enter New Course Name")
    duration = st.text_input("Enter New Course Duration")
    fee = st.text_input("Enter New Course Fee")
    update_button = st.button("Update Course")

    if update_button and course_id and (name or duration or fee):
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "UPDATE courses SET"
            update_values = []
            if name:
                query += " course_name = %s,"
                update_values.append(name)
            if duration:
                query += " duration = %s,"
                update_values.append(duration)
            if fee:
                query += " fee = %s,"
                update_values.append(fee)
            query = query.rstrip(',') + " WHERE course_id = %s"
            update_values.append(course_id)
            cursor.execute(query, tuple(update_values))
            connection.commit()
            st.success("Course updated successfully!")
            cursor.close()
            connection.close()
        else:
            st.error("Error connecting to the database.")

# Course management page
def course_management_page():
    st.title("Admin Panel - Course Management")

    # Navigation bar
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.selectbox("", ["View Courses", "Create Course", "Delete Course", "Update Course", "Logout"])

    if selected_page == "View Courses":
        view_courses_page()
    elif selected_page == "Create Course":
        create_course_page()
    elif selected_page == "Delete Course":
        delete_course_page()
    elif selected_page == "Update Course":
        update_course_page()
    elif selected_page == "Logout":
        st.session_state['logged_in'] = False
        st.success("Logged out successfully!")

# Main function
def main():
    init_session_state()

    if 'logged_in' in st.session_state and not st.session_state['logged_in']:
        login_page()
    else:
        course_management_page()

if __name__ == "__main__":
    main()
