import streamlit as st
import mysql.connector
import random
import string

# Initialize session state
def init_session_state():
    if 'current_student' not in st.session_state:
        st.session_state['current_student'] = None

# Generate a unique student ID
def generate_student_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

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

# Create login_audit table
def create_login_audit_table():
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_audit (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(8),
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

# Function to add a student to the database and assign rank based on age
def add_student_to_database(username, age, password):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            student_id = generate_student_id()
            query = "INSERT INTO students (student_id, username, age, password) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (student_id, username, age, password))
            
            # Assign rank based on age
            rank_query = """
                UPDATE students AS s1
                INNER JOIN (
                    SELECT student_id, RANK() OVER (ORDER BY age) AS age_rank
                    FROM students
                ) AS s2 ON s1.student_id = s2.student_id
                SET s1.age_rank = s2.age_rank
                WHERE s1.student_id = %s
            """
            cursor.execute(rank_query, (student_id,))
            
            connection.commit()
            cursor.close()
            connection.close()
            return student_id
        else:
            return None
    except mysql.connector.Error as err:
        st.error("Error adding student to database: {}".format(err))
        return None

# Function to fetch and display available courses
def view_courses_page():
    if not st.session_state['current_student']:
        st.warning("Please login to see courses.")
        return

    st.title("View Courses")
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM courses"
        cursor.execute(query)
        courses = cursor.fetchall()
        if courses:
            st.markdown("### Available Courses")
            for course in courses:
                st.write(f"*Course ID:* {course['course_id']}")
                st.write(f"*Course Name:* {course['course_name']}")
                st.write(f"*Duration:* {course['duration']}")
                st.write(f"*Fee:* {course['fee']}")
                button_key = f"select_button_{course['course_id']}"
                if st.button("Select", key=button_key):
                    enrollment_status = add_enrollment_to_database(st.session_state['current_student'], course['course_id'])
                    if enrollment_status == 'enrolled':
                        st.info(f"You have already enrolled in {course['course_name']}.")
                    elif enrollment_status == 'success':
                        st.success(f"Course {course['course_name']} selected!")
                st.write("")  # Add a blank line for separation
        else:
            st.write("No courses available.")
        cursor.close()
        connection.close()

# Function to display selected courses for the current student
def my_courses_page():
    if not st.session_state['current_student']:
        st.warning("Please login to see your courses.")
        return

    st.title("My Courses")
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT courses.* FROM courses INNER JOIN enrollment ON courses.course_id = enrollment.course_id WHERE enrollment.student_id = %s"
        cursor.execute(query, (st.session_state['current_student'],))
        courses = cursor.fetchall()
        if courses:
            st.markdown("### Enrolled Courses")
            for course in courses:
                st.write(f"*Course ID:* {course['course_id']}")
                st.write(f"*Course Name:* {course['course_name']}")
                st.write(f"*Duration:* {course['duration']}")
                st.write(f"*Fee:* {course['fee']}")
                st.write("")  # Add a blank line for separation
        else:
            st.write("You haven't enrolled in any courses yet.")
        cursor.close()
        connection.close()

# Function to handle student signup
def student_signup_page():
    st.title("Student Panel - Signup")
    signup_username = st.text_input("Username", key='signup_username')
    signup_age = st.number_input("Age", min_value=0, max_value=150, key='signup_age')
    signup_password = st.text_input("Password", type="password", key='signup_password')
    signup_button = st.button("Signup", key='signup_button')

    if signup_button and signup_username and signup_age and signup_password:
        # Check if the username already exists in the database
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM students WHERE username = %s"
            cursor.execute(query, (signup_username,))
            existing_student = cursor.fetchone()
            cursor.close()  # Close cursor after fetching the results
            if existing_student:
                st.warning("You already have an account. Please login.")
            else:
                student_id = add_student_to_database(signup_username, signup_age, signup_password)
                if student_id:
                    st.success("Signup successful! Your student ID is: " + student_id)
                else:
                    st.error("Signup failed. Please try again.")
            connection.close()

# Function to handle student login
def student_login_page():
    st.title("Student Panel - Login")
    login_username = st.text_input("Username:", key='login_username')
    login_password = st.text_input("Password:", type="password", key='login_password')
    login_button = st.button("Login", key='login_button')

    if login_button and login_username and login_password:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM students WHERE username = %s AND password = %s"
            cursor.execute(query, (login_username, login_password))
            student = cursor.fetchone()
            if student:
                st.session_state['current_student'] = student['student_id']
                st.success("Login successful!")
                # Log successful login
                log_successful_login(student['student_id'])
            else:
                st.error("Invalid username or password. Please try again.")
            cursor.close()  # Close cursor after fetching the results
            connection.close()

# Function to add enrollment data to the database
def add_enrollment_to_database(student_id, course_id):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO enrollment (student_id, course_id) VALUES (%s, %s)"
            cursor.execute(query, (student_id, course_id))
            connection.commit()
            cursor.close()
            connection.close()
            return 'success'
    except mysql.connector.Error as err:
        if err.errno == 1062:
            return 'enrolled'  # Student is already enrolled in this course
        st.error("Error adding enrollment to database: {}".format(err))
        return None

# Function to log successful login
def log_successful_login(student_id):
    try:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO login_audit (student_id) VALUES (%s)"
            cursor.execute(query, (student_id,))
            connection.commit()
            cursor.close()
            connection.close()
    except mysql.connector.Error as err:
        st.error("Error logging successful login: {}".format(err))

# Function to handle student logout
def student_logout():
    st.session_state['current_student'] = None
    st.success("Logout successful!")

# Main function
def main():
    init_session_state()

    create_login_audit_table()  # Create login_audit table

    st.sidebar.title("Navigation")
    nav_selection = st.sidebar.radio("Go to", ["Signup / Login", "View Courses", "My Courses", "Logout"])

    if nav_selection == "Signup / Login":
        student_signup_page()
        st.markdown("Already have an account? Click below to login.")
        student_login_page()
    elif nav_selection == "View Courses":
        view_courses_page()
    elif nav_selection == "My Courses":
        my_courses_page()
    elif nav_selection == "Logout":
        student_logout()

if __name__ == "__main__":
    main()
