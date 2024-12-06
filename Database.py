import mysql.connector
from mysql.connector import errorcode
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Database connection setup
def connect_to_db():
    """Establishes connection to the database and creates schema if needed."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="cs5330",
            password="pw5330",
            charset='utf8mb4'
        )
        
        if not conn.is_connected():
            raise mysql.connector.Error("Failed to connect to MySQL server")
            
        print("Connection established. Creating database if it doesn't exist...")
        cursor = conn.cursor(buffered=True)
        
        cursor.execute("CREATE DATABASE IF NOT EXISTS university")
        cursor.execute("USE university")
        print("Database selected.")
        
        schema_path = os.path.join(os.path.dirname(__file__), 'UniversitySchema.sql')
        execute_schema_file(conn, schema_path)
        
        return conn

    except mysql.connector.Error as err:
        handle_mysql_error(err)
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

def execute_schema_file(connection, file_path):
    """Executes the SQL schema file."""
    try:
        with open(file_path, 'r') as file:
            sql_file = file.read()
            sql_commands = sql_file.split(';')
            
            cursor = connection.cursor()
            
            for command in sql_commands:
                command = command.strip()
                if command:
                    try:
                        cursor.execute(command)
                        print(f"Successfully executed: {command[:50]}...")
                    except mysql.connector.Error as err:
                        print(f"Error executing {command[:50]}...: {err}")
                        continue
            
            connection.commit()
            print("Schema creation completed.")
    except FileNotFoundError:
        print(f"Schema file not found: {file_path}")
    except Exception as e:
        print(f"Error executing schema: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()

def handle_mysql_error(err):
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Invalid username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    elif err.errno == errorcode.CR_CONN_HOST_ERROR:
        print("Database server is not running")
    else:
        print(f"MySQL Error: {err}")

import mysql.connector
from tkinter import messagebox

def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="cs5330",
            password="pw5330",
            database="university"
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
        return None

# Basic record addition functions
def add_degree(degree_id, name, level):
    """Add a new degree program."""
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        
        # Validate level is one of the allowed values
        valid_levels = ['BA', 'BS', 'MS', 'Ph.D.', 'Cert']
        if level not in valid_levels:
            raise ValueError(f"Invalid level. Must be one of: {', '.join(valid_levels)}")
            
        cursor.execute("""
            INSERT INTO Degree (degreeID, name, level)
            VALUES (%s, %s, %s)
        """, (degree_id, name, level))
        conn.commit()
        messagebox.showinfo("Success", "Degree added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add degree: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_course(course_number, name):
    """Add a new course."""
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        
        # Validate course number format (2-4 letters + 4 digits)
        import re
        if not re.match(r'^[A-Z]{2,4}\d{4}$', course_number):
            raise ValueError("Course number must be 2-4 letters followed by 4 digits")
            
        cursor.execute("""
            INSERT INTO Course (courseNumber, name)
            VALUES (%s, %s)
        """, (course_number, name))
        conn.commit()
        messagebox.showinfo("Success", "Course added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add course: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_instructor(instructor_id, name):
    """Add a new instructor."""
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        
        # Validate instructor ID is 8 characters
        if len(instructor_id) != 8:
            raise ValueError("Instructor ID must be exactly 8 characters")
            
        cursor.execute("""
            INSERT INTO Instructor (instructorID, name)
            VALUES (%s, %s)
        """, (instructor_id, name))
        conn.commit()
        messagebox.showinfo("Success", "Instructor added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add instructor: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_goal(goal_code, degree_id, description):
    """Add a new goal for a degree program."""
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        
        # Validate goal code is exactly 4 characters
        if len(goal_code) != 4:
            raise ValueError("Goal code must be exactly 4 characters")
            
        cursor.execute("""
            INSERT INTO Goal (goalCode, degreeID, description)
            VALUES (%s, %s, %s)
        """, (goal_code, degree_id, description))
        conn.commit()
        messagebox.showinfo("Success", "Goal added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add goal: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_semester(year, term):
    """Add a new semester."""
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        
        # Validate term is one of the allowed values
        valid_terms = ['Spring', 'Summer', 'Fall']
        if term not in valid_terms:
            raise ValueError(f"Invalid term. Must be one of: {', '.join(valid_terms)}")
            
        cursor.execute("""
            INSERT INTO Semester (year, term)
            VALUES (%s, %s)
        """, (year, term))
        conn.commit()
        messagebox.showinfo("Success", "Semester added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add semester: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_section(course_number, section_id, year, term, instructor_id, enrollment_count):
    """Add a new section for a course."""
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        
        # Validate section_id is 3 characters
        if len(section_id) != 3:
            raise ValueError("Section ID must be exactly 3 characters")
            
        cursor.execute("""
            INSERT INTO Section (courseNumber, sectionID, year, term, instructorID, enrollmentCount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (course_number, section_id, year, term, instructor_id, enrollment_count))
        conn.commit()
        messagebox.showinfo("Success", "Section added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add section: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_course_degree(course_number, degree_id, is_core):
    """Associate a course with a degree program."""
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO Course_Degree (courseNumber, degreeID, isCore)
            VALUES (%s, %s, %s)
        """, (course_number, degree_id, is_core))
        conn.commit()
        messagebox.showinfo("Success", "Course-Degree association added successfully.")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add course-degree association: {str(e)}")
    finally:
        if conn:
            conn.close()

def gui():
    root = tk.Tk()
    root.title("University Database")

    # Create Notebook for tabs
    tabs = ttk.Notebook(root)

    # Degree Tab
    degree_tab = ttk.Frame(tabs)
    tabs.add(degree_tab, text="Add Degree")

    ttk.Label(degree_tab, text="Degree ID:").grid(row=0, column=0, padx=5, pady=5)
    degree_id_entry = ttk.Entry(degree_tab)
    degree_id_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(degree_tab, text="Name:").grid(row=1, column=0, padx=5, pady=5)
    degree_name_entry = ttk.Entry(degree_tab)
    degree_name_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(degree_tab, text="Level:").grid(row=2, column=0, padx=5, pady=5)
    degree_level_entry = ttk.Entry(degree_tab)
    degree_level_entry.grid(row=2, column=1, padx=5, pady=5)

    def handle_add_degree():
        add_degree(degree_id_entry.get(), degree_name_entry.get(), degree_level_entry.get())

    ttk.Button(degree_tab, text="Add Degree", command=handle_add_degree).grid(row=3, column=0, columnspan=2, pady=10)

    # Course Tab
    course_tab = ttk.Frame(tabs)
    tabs.add(course_tab, text="Add Course")

    ttk.Label(course_tab, text="Course Number:").grid(row=0, column=0, padx=5, pady=5)
    course_number_entry = ttk.Entry(course_tab)
    course_number_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(course_tab, text="Course Name:").grid(row=1, column=0, padx=5, pady=5)
    course_name_entry = ttk.Entry(course_tab)
    course_name_entry.grid(row=1, column=1, padx=5, pady=5)

    def handle_add_course():
        add_course(course_number_entry.get(), course_name_entry.get())

    ttk.Button(course_tab, text="Add Course", command=handle_add_course).grid(row=2, column=0, columnspan=2, pady=10)

    # Instructor Tab
    instructor_tab = ttk.Frame(tabs)
    tabs.add(instructor_tab, text="Add Instructor")

    ttk.Label(instructor_tab, text="Instructor ID:").grid(row=0, column=0, padx=5, pady=5)
    instructor_id_entry = ttk.Entry(instructor_tab)
    instructor_id_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(instructor_tab, text="Instructor Name:").grid(row=1, column=0, padx=5, pady=5)
    instructor_name_entry = ttk.Entry(instructor_tab)
    instructor_name_entry.grid(row=1, column=1, padx=5, pady=5)

    def handle_add_instructor():
        add_instructor(instructor_id_entry.get(), instructor_name_entry.get())

    ttk.Button(instructor_tab, text="Add Instructor", command=handle_add_instructor).grid(row=2, column=0, columnspan=2, pady=10)

    # Goal Tab
    goal_tab = ttk.Frame(tabs)
    tabs.add(goal_tab, text="Add Goal")

    ttk.Label(goal_tab, text="Goal Code:").grid(row=0, column=0, padx=5, pady=5)
    goal_code_entry = ttk.Entry(goal_tab)
    goal_code_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(goal_tab, text="Degree ID:").grid(row=1, column=0, padx=5, pady=5)
    goal_degree_id_entry = ttk.Entry(goal_tab)
    goal_degree_id_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(goal_tab, text="Description:").grid(row=2, column=0, padx=5, pady=5)
    goal_description_entry = ttk.Entry(goal_tab)
    goal_description_entry.grid(row=2, column=1, padx=5, pady=5)

    def handle_add_goal():
        add_goal(goal_code_entry.get(), goal_degree_id_entry.get(), goal_description_entry.get())

    ttk.Button(goal_tab, text="Add Goal", command=handle_add_goal).grid(row=3, column=0, columnspan=2, pady=10)

    # Semester Tab
    semester_tab = ttk.Frame(tabs)
    tabs.add(semester_tab, text="Add Semester")

    ttk.Label(semester_tab, text="Year:").grid(row=0, column=0, padx=5, pady=5)
    semester_year_entry = ttk.Entry(semester_tab)
    semester_year_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(semester_tab, text="Term:").grid(row=1, column=0, padx=5, pady=5)
    semester_term_entry = ttk.Entry(semester_tab)
    semester_term_entry.grid(row=1, column=1, padx=5, pady=5)

    def handle_add_semester():
        add_semester(semester_year_entry.get(), semester_term_entry.get())

    ttk.Button(semester_tab, text="Add Semester", command=handle_add_semester).grid(row=2, column=0, columnspan=2, pady=10)

    # Section Tab
    section_tab = ttk.Frame(tabs)
    tabs.add(section_tab, text="Add Section")

    ttk.Label(section_tab, text="Course Number:").grid(row=0, column=0, padx=5, pady=5)
    section_course_number_entry = ttk.Entry(section_tab)
    section_course_number_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(section_tab, text="Section ID:").grid(row=1, column=0, padx=5, pady=5)
    section_id_entry = ttk.Entry(section_tab)
    section_id_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(section_tab, text="Year:").grid(row=2, column=0, padx=5, pady=5)
    section_year_entry = ttk.Entry(section_tab)
    section_year_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(section_tab, text="Term:").grid(row=3, column=0, padx=5, pady=5)
    section_term_entry = ttk.Entry(section_tab)
    section_term_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(section_tab, text="Instructor ID:").grid(row=4, column=0, padx=5, pady=5)
    section_instructor_id_entry = ttk.Entry(section_tab)
    section_instructor_id_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Label(section_tab, text="Enrollment Count:").grid(row=5, column=0, padx=5, pady=5)
    section_enrollment_count_entry = ttk.Entry(section_tab)
    section_enrollment_count_entry.grid(row=5, column=1, padx=5, pady=5)

    def handle_add_section():
        add_section(
            section_course_number_entry.get(),
            section_id_entry.get(),
            section_year_entry.get(),
            section_term_entry.get(),
            section_instructor_id_entry.get(),
            section_enrollment_count_entry.get()
        )

    ttk.Button(section_tab, text="Add Section", command=handle_add_section).grid(row=6, column=0, columnspan=2, pady=10)

    # Course-Degree Association Tab
    course_degree_tab = ttk.Frame(tabs)
    tabs.add(course_degree_tab, text="Associate Course to Degree")

    ttk.Label(course_degree_tab, text="Course Number:").grid(row=0, column=0, padx=5, pady=5)
    course_degree_course_number_entry = ttk.Entry(course_degree_tab)
    course_degree_course_number_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(course_degree_tab, text="Degree ID:").grid(row=1, column=0, padx=5, pady=5)
    course_degree_degree_id_entry = ttk.Entry(course_degree_tab)
    course_degree_degree_id_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(course_degree_tab, text="Is Core (1=True, 0=False):").grid(row=2, column=0, padx=5, pady=5)
    course_degree_is_core_entry = ttk.Entry(course_degree_tab)
    course_degree_is_core_entry.grid(row=2, column=1, padx=5, pady=5)

    def handle_add_course_degree():
        add_course_degree(
            course_degree_course_number_entry.get(),
            course_degree_degree_id_entry.get(),
            int(course_degree_is_core_entry.get())
        )

    ttk.Button(course_degree_tab, text="Add Association", command=handle_add_course_degree).grid(row=3, column=0, columnspan=2, pady=10)

    # Pack Tabs
    tabs.pack(expand=1, fill="both")
    root.mainloop()
        
# Main section
if __name__ == "__main__":
    gui()

#checking push