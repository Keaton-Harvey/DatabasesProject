import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode

def connect_to_db(schema_file_path):
    try:
        # Connect to MySQL server (defaults to localhost:3306)
        conn = mysql.connector.connect(
            user="cs5330",
            password="pw5330",
        )
        
        if conn.is_connected():
            print("Connection established. Reading schema...")
            
            # Execute the schema file
            execute_schema_file(conn, schema_file_path)
            return conn
        else:
            messagebox.showerror("Database Connection Error", "Unable to connect to the database server.")
            return None

    except mysql.connector.Error as err:
        # Handle specific MySQL errors
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Database Connection Error", "Invalid username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Database Connection Error", "Database does not exist.")
        elif err.errno == errorcode.CR_CONN_HOST_ERROR:
            messagebox.showerror("Database Connection Error", "Unable to connect to the database server. Check if the server is running.")
        else:
            messagebox.showerror("Database Connection Error", f"An unexpected error occurred: {str(err)}")
        return None
    except Exception as e:
        # Handle unexpected exceptions
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        return None


def execute_schema_file(connection, file_path):
    """
    Executes an SQL schema file on the given database connection.
    
    Parameters:
        connection: A MySQL connection object.
        file_path (str): Path to the SQL schema file to execute.
    """
    try:
        cursor = connection.cursor()
        print(f"Reading schema from: {file_path}")

        # Open and read the schema file
        with open(file_path, 'r') as file:
            sql_script = file.read()

        # Execute each SQL statement in the script
        for statement in sql_script.split(';'):  # Split by semicolon for individual statements
            if statement.strip():  # Skip empty lines/statements
                cursor.execute(statement)
                print(f"Executed: {statement.strip()}")

        print("Schema successfully executed.")
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error executing schema: {err}")
    except FileNotFoundError:
        print(f"Schema file not found: {file_path}")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Queries:

def get_courses_by_degree(degree_id):
    if not degree_id:
        raise ValueError("Degree ID cannot be empty.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT C.courseNumber, C.name, DC.isCore
            FROM Degree_Course DC
            JOIN Course C ON DC.courseNumber = C.courseNumber
            WHERE DC.degreeID = %s;
        """, (degree_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()

def get_sections_by_time_range(start_year, end_year):
    if not start_year.isdigit() or not end_year.isdigit():
        raise ValueError("Start and End years must be numeric.")
    if int(start_year) > int(end_year):
        raise ValueError("Start year cannot be greater than End year.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT S.courseNumber, S.sectionID, Sem.year, Sem.term
            FROM Section S
            JOIN Semester Sem ON S.semesterID = Sem.semesterID
            WHERE Sem.year BETWEEN %s AND %s
            ORDER BY Sem.year, Sem.term;
        """, (start_year, end_year))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()

def get_courses_by_goal(goal_code):
    if not goal_code:
        raise ValueError("Goal Code cannot be empty.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT G.goalCode, G.description, C.courseNumber, C.name
            FROM Goal G
            JOIN Degree_Course DC ON G.degreeID = DC.degreeID
            JOIN Course C ON DC.courseNumber = C.courseNumber
            WHERE G.goalCode = %s;
        """, (goal_code,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()


def get_goals_by_degree(degree_id):
    if not degree_id:
        raise ValueError("Degree ID cannot be empty.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT goalCode, description
            FROM Goal
            WHERE degreeID = %s;
        """, (degree_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()

def get_sections_by_course(course_number, start_year, end_year):
    if not course_number:
        raise ValueError("Course Number cannot be empty.")
    if not start_year.isdigit() or not end_year.isdigit():
        raise ValueError("Start and End years must be numeric.")
    if int(start_year) > int(end_year):
        raise ValueError("Start year cannot be greater than End year.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT S.sectionID, Sem.year, Sem.term
            FROM Section S
            JOIN Semester Sem ON S.semesterID = Sem.semesterID
            WHERE S.courseNumber = %s AND Sem.year BETWEEN %s AND %s
            ORDER BY Sem.year, Sem.term;
        """, (course_number, start_year, end_year))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()

def get_sections_by_instructor(instructor_id, start_year, end_year):
    if not instructor_id:
        raise ValueError("Instructor ID cannot be empty.")
    if not start_year.isdigit() or not end_year.isdigit():
        raise ValueError("Start and End years must be numeric.")
    if int(start_year) > int(end_year):
        raise ValueError("Start year cannot be greater than End year.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT S.courseNumber, S.sectionID, Sem.year, Sem.term
            FROM Section S
            JOIN Semester Sem ON S.semesterID = Sem.semesterID
            WHERE S.instructorID = %s AND Sem.year BETWEEN %s AND %s
            ORDER BY Sem.year, Sem.term;
        """, (instructor_id, start_year, end_year))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()

def get_evaluation_status(semester_id):
    if not semester_id:
        raise ValueError("Semester ID cannot be empty.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT S.courseNumber, S.sectionID, 
                   CASE 
                       WHEN E.courseNumber IS NULL THEN 'Not Entered'
                       WHEN E.improvementNote IS NULL THEN 'Partially Entered'
                       ELSE 'Fully Entered'
                   END AS evaluation_status
            FROM Section S
            LEFT JOIN Evaluation E 
            ON S.courseNumber = E.courseNumber AND S.sectionID = E.sectionID
            WHERE S.semesterID = %s;
        """, (semester_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()

def get_high_passing_sections(semester_id, percentage_threshold):
    if not semester_id:
        raise ValueError("Semester ID cannot be empty.")
    if not isinstance(percentage_threshold, (int, float)):
        raise ValueError("Percentage threshold must be a number.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT S.courseNumber, S.sectionID, 
                   ((E.gradeCountA + E.gradeCountB + E.gradeCountC) * 100.0) /
                   (E.gradeCountA + E.gradeCountB + E.gradeCountC + E.gradeCountF) AS pass_percentage
            FROM Section S
            JOIN Evaluation E ON S.courseNumber = E.courseNumber AND S.sectionID = E.sectionID
            WHERE S.semesterID = %s AND 
                  ((E.gradeCountA + E.gradeCountB + E.gradeCountC) * 100.0) /
                  (E.gradeCountA + E.gradeCountB + E.gradeCountC + E.gradeCountF) >= %s;
        """, (semester_id, percentage_threshold))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred: {err}")
        return []
    finally:
        if conn:
            conn.close()

# Data Entry

def add_degree(degree_id, name, level):
    if not degree_id or not name or not level:
        raise ValueError("Degree ID, Name, and Level are required.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Degree (degreeID, name, level)
            VALUES (%s, %s, %s)
        """, (degree_id, name, level))
        conn.commit()
        messagebox.showinfo("Success", "Degree added successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding degree: {err}")
    finally:
        if conn:
            conn.close()

def add_course(course_number, name):
    if not course_number or not name:
        raise ValueError("Course Number and Name are required.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Course (courseNumber, name)
            VALUES (%s, %s)
        """, (course_number, name))
        conn.commit()
        messagebox.showinfo("Success", "Course added successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding course: {err}")
    finally:
        if conn:
            conn.close()

def add_instructor(instructor_id, name):
    if not instructor_id or not name:
        raise ValueError("Instructor ID and Name are required.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Instructor (instructorID, name)
            VALUES (%s, %s)
        """, (instructor_id, name))
        conn.commit()
        messagebox.showinfo("Success", "Instructor added successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding instructor: {err}")
    finally:
        if conn:
            conn.close()

def add_section(course_number, section_id, semester_id, instructor_id, enrollment_count):
    if not course_number or not section_id or not semester_id or not instructor_id:
        raise ValueError("Course Number, Section ID, Semester ID, and Instructor ID are required.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Section (courseNumber, sectionID, semesterID, instructorID, enrollmentCount)
            VALUES (%s, %s, %s, %s, %s)
        """, (course_number, section_id, semester_id, instructor_id, enrollment_count))
        conn.commit()
        messagebox.showinfo("Success", "Section added successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding section: {err}")
    finally:
        if conn:
            conn.close()

def add_goal(goal_code, degree_id, description):
    if not goal_code or not degree_id or not description:
        raise ValueError("Goal Code, Degree ID, and Description are required.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Goal (goalCode, degreeID, description)
            VALUES (%s, %s, %s)
        """, (goal_code, degree_id, description))
        conn.commit()
        messagebox.showinfo("Success", "Goal added successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding goal: {err}")
    finally:
        if conn:
            conn.close()

def associate_course_with_goal(course_number, goal_code, degree_id):
    if not course_number or not goal_code or not degree_id:
        raise ValueError("Course Number, Goal Code, and Degree ID are required.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Degree_Course (courseNumber, degreeID, goalCode)
            VALUES (%s, %s, %s)
        """, (course_number, degree_id, goal_code))
        conn.commit()
        messagebox.showinfo("Success", "Course associated with goal successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error associating course with goal: {err}")
    finally:
        if conn:
            conn.close()

def duplicate_evaluation(source_degree_id, target_degree_id):
    if not source_degree_id or not target_degree_id:
        raise ValueError("Source and Target Degree IDs are required.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Evaluation (courseNumber, sectionID, semesterID, goalCode, evaluationType, gradeCountA, gradeCountB, gradeCountC, gradeCountF, improvementNote)
            SELECT courseNumber, sectionID, semesterID, goalCode, evaluationType, gradeCountA, gradeCountB, gradeCountC, gradeCountF, improvementNote
            FROM Evaluation
            WHERE degreeID = %s
        """, (source_degree_id,))
        conn.commit()
        messagebox.showinfo("Success", "Evaluations duplicated successfully.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error duplicating evaluations: {err}")
    finally:
        if conn:
            conn.close()

# Fetch semesters
def fetch_semesters():
    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT semesterID, year, term FROM Semester")
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred while fetching semesters: {err}")
        return []
    finally:
        if conn:
            conn.close()

# Fetch instructors
def fetch_instructors():
    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT instructorID, name FROM Instructor")
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred while fetching instructors: {err}")
        return []
    finally:
        if conn:
            conn.close()

# Fetch sections taught by instructor in a semester
def fetch_sections(instructor_id, semester_id):
    if not instructor_id:
        raise ValueError("Instructor ID cannot be empty.")
    if not semester_id:
        raise ValueError("Semester ID cannot be empty.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT S.courseNumber, S.sectionID, C.name
            FROM Section S
            JOIN Course C ON S.courseNumber = C.courseNumber
            WHERE S.instructorID = %s AND S.semesterID = %s
        """, (instructor_id, semester_id))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred while fetching sections: {err}")
        return []
    finally:
        if conn:
            conn.close()

def fetch_evaluation_status(semester_id):
    if not semester_id:
        raise ValueError("Semester ID cannot be empty.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT S.courseNumber, S.sectionID, 
                   CASE 
                       WHEN E.courseNumber IS NULL THEN 'Not Entered'
                       WHEN E.improvementNote IS NULL THEN 'Partially Entered'
                       ELSE 'Fully Entered'
                   END AS evaluation_status
            FROM Section S
            LEFT JOIN Evaluation E 
            ON S.courseNumber = E.courseNumber AND S.sectionID = E.sectionID
            WHERE S.semesterID = %s;
        """, (semester_id,))
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred while fetching evaluation status: {err}")
        return []
    finally:
        if conn:
            conn.close()

# Add or update evaluation
def save_evaluation(data):
    if not isinstance(data, list) or not all(isinstance(entry, tuple) for entry in data):
        raise ValueError("Data must be a list of tuples.")

    conn = None
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        for entry in data:
            if len(entry) != 10:
                raise ValueError("Each entry must have exactly 10 values.")
            cursor.execute("""
                INSERT INTO Evaluation (courseNumber, sectionID, semesterID, goalCode, evaluationType, gradeCountA, gradeCountB, gradeCountC, gradeCountF, improvementNote)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                evaluationType = VALUES(evaluationType),
                gradeCountA = VALUES(gradeCountA),
                gradeCountB = VALUES(gradeCountB),
                gradeCountC = VALUES(gradeCountC),
                gradeCountF = VALUES(gradeCountF),
                improvementNote = VALUES(improvementNote)
            """, entry)
        conn.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Query Error", f"An error occurred while saving evaluations: {err}")
    except ValueError as ve:
        messagebox.showerror("Data Validation Error", f"Validation failed: {ve}")
    finally:
        if conn:
            conn.close()

def main_gui():
    def load_courses_by_degree():
        degree_id = degree_combobox.get().split(":")[0]
        courses = get_courses_by_degree(degree_id)
        tree.delete(*tree.get_children())
        for course in courses:
            tree.insert("", "end", values=course)

    def load_sections_by_time():
        start_year = start_year_entry.get()
        end_year = end_year_entry.get()
        sections = get_sections_by_time_range(start_year, end_year)
        tree.delete(*tree.get_children())
        for section in sections:
            tree.insert("", "end", values=section)

    def load_goals_by_degree():
        degree_id = degree_combobox.get().split(":")[0]
        goals = get_goals_by_degree(degree_id)
        tree.delete(*tree.get_children())
        for goal in goals:
            tree.insert("", "end", values=goal)

    def load_courses_by_goal():
        goal_code = goal_code_entry.get()
        courses = get_courses_by_goal(goal_code)
        tree.delete(*tree.get_children())
        for course in courses:
            tree.insert("", "end", values=course)

    def query_evaluation_status():
        semester_id = semester_combobox.get().split(":")[0]
        evaluations = get_evaluation_status(semester_id)
        tree.delete(*tree.get_children())
        for eval in evaluations:
            tree.insert("", "end", values=eval)

    def query_high_passing_sections():
        semester_id = semester_combobox.get().split(":")[0]
        percentage_threshold = float(percentage_entry.get())
        sections = get_high_passing_sections(semester_id, percentage_threshold)
        tree.delete(*tree.get_children())
        for section in sections:
            tree.insert("", "end", values=section)

    # Main window
    root = tk.Tk()
    root.title("Database Queries and Evaluation")

    # Degree selection
    tk.Label(root, text="Select Degree:").grid(row=0, column=0, padx=5, pady=5)
    degrees = fetch_semesters()  # Replace with actual degree-fetching logic
    degree_combobox = ttk.Combobox(root, values=[f"{d[0]}: {d[1]}" for d in degrees])
    degree_combobox.grid(row=0, column=1, padx=5, pady=5)

    # Time range inputs
    tk.Label(root, text="Start Year:").grid(row=1, column=0, padx=5, pady=5)
    start_year_entry = tk.Entry(root)
    start_year_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(root, text="End Year:").grid(row=2, column=0, padx=5, pady=5)
    end_year_entry = tk.Entry(root)
    end_year_entry.grid(row=2, column=1, padx=5, pady=5)

    # Goal code input
    tk.Label(root, text="Goal Code:").grid(row=3, column=0, padx=5, pady=5)
    goal_code_entry = tk.Entry(root)
    goal_code_entry.grid(row=3, column=1, padx=5, pady=5)

    # Semester selection
    tk.Label(root, text="Select Semester:").grid(row=4, column=0, padx=5, pady=5)
    semesters = fetch_semesters()
    semester_combobox = ttk.Combobox(root, values=[f"{s[0]}: {s[1]} {s[2]}" for s in semesters])
    semester_combobox.grid(row=4, column=1, padx=5, pady=5)

    # Percentage input for evaluation query
    tk.Label(root, text="Pass Percentage:").grid(row=5, column=0, padx=5, pady=5)
    percentage_entry = tk.Entry(root)
    percentage_entry.grid(row=5, column=1, padx=5, pady=5)

    # Buttons for queries
    tk.Button(root, text="Load Courses by Degree", command=load_courses_by_degree).grid(row=6, column=0, padx=5, pady=5)
    tk.Button(root, text="Load Sections by Time", command=load_sections_by_time).grid(row=6, column=1, padx=5, pady=5)
    tk.Button(root, text="Load Goals by Degree", command=load_goals_by_degree).grid(row=7, column=0, padx=5, pady=5)
    tk.Button(root, text="Load Courses by Goal", command=load_courses_by_goal).grid(row=7, column=1, padx=5, pady=5)
    tk.Button(root, text="Evaluation Status", command=query_evaluation_status).grid(row=8, column=0, padx=5, pady=5)
    tk.Button(root, text="High Passing Sections", command=query_high_passing_sections).grid(row=8, column=1, padx=5, pady=5)

    # Results Treeview
    tree = ttk.Treeview(root, columns=("Col1", "Col2", "Col3"), show="headings")
    tree.grid(row=9, column=0, columnspan=2, padx=5, pady=5)
    tree.heading("Col1", text="Column 1")
    tree.heading("Col2", text="Column 2")
    tree.heading("Col3", text="Column 3")

    root.mainloop()

# Main application
main_gui()
