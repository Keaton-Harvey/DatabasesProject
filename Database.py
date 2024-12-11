import mysql.connector
from mysql.connector import errorcode
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Database connection setup
def connect_to_db(run_schema=False):
    """Establish connection to the database, creating it if necessary."""
    try:
        # Connect without specifying the database
        conn = mysql.connector.connect(
            host="localhost",
            user="cs5330",
            password="pw5330",
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # Try to select the 'university' database
        try:
            cursor.execute("USE university;")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database 'university' not found. Creating it...")
                cursor.execute("CREATE DATABASE university;")
                cursor.execute("USE university;")
                
                # After creating the database, run the schema
                print("Executing schema file to create tables...")
                schema_path = os.path.join(os.path.dirname(__file__), 'UniversitySchema.sql')
                execute_schema_file(conn, schema_path)
            else:
                raise

        # If run_schema is True, we explicitly run the schema again to ensure tables exist
        # (For example, to re-create tables if needed)
        if run_schema:
            schema_path = os.path.join(os.path.dirname(__file__), 'UniversitySchema.sql')
            execute_schema_file(conn, schema_path)

        return conn

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
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

# Basic record addition functions
def add_degree(degree_id, name, level):
    """
    Add a new degree program.
    
    Parameters:
        degree_id (str): The unique identifier for the degree
        name (str): The name of the degree program
        level (str): The academic level (BA, BS, MS, Ph.D., Cert)

     Returns:
        None
    """
    import re
    
    # Ensure all required fields are provided
    if not degree_id.strip() or not name.strip() or not level.strip():
        messagebox.showerror("Input Error", "All fields (Degree ID, Name, and Level) are required.")
        return
    
    # Validate degree name contains only alphabetic characters and spaces
    if not re.match(r'^[A-Za-z\s]+$', name):
        messagebox.showerror("Validation Error", "Degree name must contain only alphabetic characters and spaces.")
        return

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
    
    except mysql.connector.IntegrityError as e:
        if e.errno == errorcode.ER_DUP_ENTRY:
            if 'unique_name_level' in str(e):
                messagebox.showerror("Database Error", "A degree with this name and level already exists.")
            else:
                messagebox.showerror("Database Error", "A degree with this ID already exists.")
        else:
            messagebox.showerror("Database Error", f"Failed to add degree: {str(e)}")
    except ValueError as ve:
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Failed to add degree: {str(e)}")
    finally:
        if conn:
            conn.close()



def add_course(course_number, name):
    import re
    """
    Add a new course to the database.

    Parameters:
        course_number (str): The unique course number.
        name (str): The name of the course.

    Returns:
        None
    """
    # Ensure both fields are provided
    if not course_number.strip() or not name.strip():
        messagebox.showerror("Input Error", "Both fields (Course Number and Name) are required.")
        return
    
    # Validate course name contains only alphabetic characters and spaces
    if not re.match(r'^[A-Za-z\s]+$', name):
        messagebox.showerror("Validation Error", "Course name must contain only alphabetic characters and spaces.")
        return

    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()

        # Validate course number format (2-4 letters + 4 digits)
        if not re.match(r'^[A-Z]{2,4}\d{4}$', course_number):
            raise ValueError("Course number must be 2-4 uppercase letters followed by 4 digits.")

        cursor.execute("""
            INSERT INTO Course (courseNumber, name)
            VALUES (%s, %s)
        """, (course_number, name))
        conn.commit()
        messagebox.showinfo("Success", "Course added successfully.")
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to add course: {str(e)}")
    finally:
        if conn:
            conn.close()


def add_instructor(instructor_id, name):
    import re
    """
    Add a new instructor to the database.

    Parameters:
        instructor_id (str): The unique ID of the instructor.
        name (str): The name of the instructor.

    Returns:
        None
    """
    # Ensure both fields are provided
    if not instructor_id.strip() or not name.strip():
        messagebox.showerror("Input Error", "Both fields (Instructor ID and Name) are required.")
        return

    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()

        # Ensure the input is validated as a string
        if not isinstance(instructor_id, str):
            instructor_id = str(instructor_id)

        # Validate instructor ID is exactly 8 numeric characters
        if not re.match(r'^\d{8}$', instructor_id):
            raise ValueError("Instructor ID must be exactly 8 numeric characters.")

        # Insert into the database
        cursor.execute("""
            INSERT INTO Instructor (instructorID, name)
            VALUES (%s, %s)
        """, (instructor_id, name))
        conn.commit()
        messagebox.showinfo("Success", "Instructor added successfully.")
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to add instructor: {str(e)}")
    finally:
        if conn:
            conn.close()


def add_goal(goal_code, degree_id, description):
    """
    Add a new goal to the database.

    Parameters:
        goal_code (str): The unique code of the goal.
        degree_id (str): The ID of the associated degree.
        description (str): A text description of the goal.

    Returns:
        None
    """
    # Ensure all fields are provided
    if not goal_code.strip() or not degree_id.strip() or not description.strip():
        messagebox.showerror("Input Error", "All fields (Goal Code, Degree ID, and Description) are required.")
        return
    if len(goal_code) != 4:
        messagebox.showerror("Validation Error", "Goal code must be exactly 4 characters.")
        return
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()

        import re
        if not re.match(r"^[A-Za-z]\d{3}$", goal_code):
            raise ValueError("Goal code must be any single character followed by 3 positive numbers.")

        # Check if the degree ID exists
        cursor.execute("SELECT 1 FROM Degree WHERE degreeID = %s", (degree_id,))
        if cursor.fetchone() is None:
            messagebox.showerror("Validation Error", f"No matching Degree ID found for: {degree_id}")
            return

        # Insert the goal
        cursor.execute("""
            INSERT INTO Goal (goalCode, degreeID, description)
            VALUES (%s, %s, %s)
        """, (goal_code, degree_id, description))
        conn.commit()
        messagebox.showinfo("Success", "Goal added successfully.")
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to add goal: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_semester(year, term):
    """
    Add a new semester to the database.

    Parameters:
        year (str): The year of the semester.
        term (str): The term of the semester (e.g., Spring, Summer, Fall).

    Returns:
        None
    """
    # Ensure both fields are provided
    if not year.strip() or not term.strip():
        messagebox.showerror("Input Error", "Both fields (Year and Term) are required.")
        return
    if not year.isdigit() or len(year) != 4:
        messagebox.showerror("Validation Error", "Year must be a valid 4-digit number.")
        return
    valid_terms = ['Spring', 'Summer', 'Fall']
    if term not in valid_terms:
        messagebox.showerror("Validation Error", f"Invalid term. Must be one of: {', '.join(valid_terms)}.")
        return
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Semester (year, term)
            VALUES (%s, %s)
        """, (year, term))
        conn.commit()
        messagebox.showinfo("Success", "Semester added successfully.")
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to add semester: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_section(course_number, section_id, year, term, instructor_id, enrollment_count):
    """
    Add a new section to the database.

    Parameters:
        course_number (str): The course number associated with the section.
        section_id (str): The unique ID of the section (3 characters).
        year (str): The year of the semester.
        term (str): The term of the semester (e.g., Spring, Summer, Fall).
        instructor_id (str): The ID of the instructor teaching the section.
        enrollment_count (str): The number of students enrolled in the section.

    Returns:
        None
    """
    # Ensure all fields are provided
    if not course_number.strip() or not section_id.strip() or not year.strip() or not term.strip() or not instructor_id.strip() or not enrollment_count.strip():
        messagebox.showerror("Input Error", "All fields are required to add a section.")
        return
    if len(section_id) != 3:
        messagebox.showerror("Validation Error", "Section ID must be exactly 3 characters.")
        return
    if not year.isdigit() or len(year) != 4:
        messagebox.showerror("Validation Error", "Year must be a valid 4-digit number.")
        return
    valid_terms = ['Spring', 'Summer', 'Fall']
    if term not in valid_terms:
        messagebox.showerror("Validation Error", f"Invalid term. Must be one of: {', '.join(valid_terms)}.")
        return
    if not enrollment_count.isdigit() or int(enrollment_count) < 0:
        messagebox.showerror("Validation Error", "Enrollment count must be a non-negative integer.")
        return
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()

        # Validate section_id is exactly 3 characters
        if len(section_id) != 3:
            raise ValueError("Section ID must be exactly 3 characters.")

        # Validate year is a four-digit number
        if not year.isdigit() or len(year) != 4:
            raise ValueError("Year must be a valid 4-digit number.")

        # Validate term is one of the allowed values
        valid_terms = ['Spring', 'Summer', 'Fall']
        if term not in valid_terms:
            raise ValueError(f"Invalid term. Must be one of: {', '.join(valid_terms)}.")
        
        # Check if instructor ID exists
        cursor.execute("SELECT COUNT(*) FROM Instructor WHERE instructorID = %s", (instructor_id,))
        instructor_exists = cursor.fetchone()[0]
        if not instructor_exists:
            raise ValueError(f"No match found for Instructor ID: {instructor_id}")

        # Check if course number exists
        cursor.execute("SELECT COUNT(*) FROM Course WHERE courseNumber = %s", (course_number,))
        course_exists = cursor.fetchone()[0]
        if not course_exists:
            raise ValueError(f"No match found for Course Number: {course_number}")

        # Validate enrollment_count is a non-negative integer
        if not enrollment_count.isdigit() or int(enrollment_count) < 0:
            raise ValueError("Enrollment count must be a non-negative integer.")

        cursor.execute("""
            INSERT INTO Section (courseNumber, sectionID, year, term, instructorID, enrollmentCount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (course_number, section_id, year, term, instructor_id, int(enrollment_count)))
        conn.commit()
        cursor.execute("""
                SELECT cd.degreeID, g.goalCode
                FROM Course_Degree cd
                JOIN Goal g ON cd.degreeID = g.degreeID
                WHERE cd.courseNumber = %s
            """, (course_number,))
        degree_goals = cursor.fetchall()

            # For each degree-goal pair, insert an Evaluation record if not already existing
        for (deg_id, goal_code) in degree_goals:
            cursor.execute("""
                INSERT IGNORE INTO Evaluation (courseNumber, sectionID, year, term, degreeID, goalCode, gradeCountA, gradeCountB, gradeCountC, gradeCountF)
                VALUES (%s, %s, %s, %s, %s, %s, 0,0,0,0)
            """, (course_number, section_id, year, term, deg_id, goal_code))

        conn.commit()

        messagebox.showinfo("Success", "Section added successfully.")
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to add section: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_course_degree(course_number, degree_id, is_core):
    """Associate a course with a degree program.
    
    Parameters:
        course_number (str): The unique identifier of the course to be associated
        degree_id (str): The unique identifier of the degree program
        is_core (bool): Indicates whether the course is a core course for the degree

    Returns:
        None
    """
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish a database connection.")
        cursor = conn.cursor()

        # Check if the course exists
        cursor.execute("SELECT 1 FROM Course WHERE courseNumber = %s", (course_number,))
        course_exists = cursor.fetchone()
        if not course_exists:
            messagebox.showerror("Error", f"No matching course found for Course Number: {course_number}")
            return

        # Check if the degree exists
        cursor.execute("SELECT 1 FROM Degree WHERE degreeID = %s", (degree_id,))
        degree_exists = cursor.fetchone()
        if not degree_exists:
            messagebox.showerror("Error", f"No matching degree found for Degree ID: {degree_id}")
            return

        # Insert the course-degree association
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


def associate_course_with_goal(course_number, degree_id, goal_code):
    """
    Associate a course with a goal for a specific degree.

    Parameters:
        course_number (str): The course number to associate.
        degree_id (str): The degree ID to associate.
        goal_code (str): The goal code to associate.

    Returns:
        None
    """
    # Ensure all fields are provided
    if not course_number.strip() or not degree_id.strip() or not goal_code.strip():
        messagebox.showerror("Input Error", "All fields (Course Number, Degree ID, Goal Code) are required.")
        return

    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish database connection")
        cursor = conn.cursor()

        # Check if the course exists
        cursor.execute("""
            SELECT 1 FROM Course WHERE courseNumber = %s
        """, (course_number,))
        if not cursor.fetchone():
            raise ValueError(f"No matching course found for Course Number: {course_number}.")

        # Check if the degree exists
        cursor.execute("""
            SELECT 1 FROM Degree WHERE degreeID = %s
        """, (degree_id,))
        if not cursor.fetchone():
            raise ValueError(f"No matching degree found for Degree ID: {degree_id}.")

        # Check if the goal exists for the degree
        cursor.execute("""
            SELECT 1 FROM Goal WHERE goalCode = %s AND degreeID = %s
        """, (goal_code, degree_id))
        if not cursor.fetchone():
            raise ValueError(f"No matching goal found for Goal Code: {goal_code} and Degree ID: {degree_id}.")

        # Check if the course is associated with the degree
        cursor.execute("""
            SELECT 1 FROM Course_Degree 
            WHERE courseNumber = %s AND degreeID = %s
        """, (course_number, degree_id))
        if not cursor.fetchone():
            raise ValueError(f"The course {course_number} is not associated with the degree {degree_id}.")

        # Insert the association into the Evaluation table
        cursor.execute("""
            INSERT INTO Evaluation (courseNumber, sectionID, year, term, degreeID, goalCode)
            SELECT DISTINCT s.courseNumber, s.sectionID, s.year, s.term, %s, %s
            FROM Section s
            WHERE s.courseNumber = %s
        """, (degree_id, goal_code, course_number))

        conn.commit()
        messagebox.showinfo("Success", "Course-Goal association added successfully.")
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to associate course with goal: {str(e)}")
    finally:
        if conn:
            conn.close()

def add_course_to_semester(course_number, section_id, year, term, instructor_id, enrollment_count=0):
    """
    Add a course section to a semester with prerequisite checks.

    Parameters:
        course_number (str): The course number.
        section_id (str): The section ID.
        year (str): The year.
        term (str): The term (e.g., Spring, Summer, Fall).
        instructor_id (str): The instructor ID.
        enrollment_count (int): The number of students enrolled.

    Returns:
        None
    """
    # Ensure all fields are provided
    if not course_number.strip() or not section_id.strip() or not year.strip() or not term.strip() or not instructor_id.strip():
        messagebox.showerror("Input Error", "All fields (Course Number, Section ID, Year, Term, and Instructor ID) are required.")
        return
    if not year.isdigit() or len(year) != 4:
        messagebox.showerror("Validation Error", "Year must be a valid 4-digit number.")
        return
    valid_terms = ['Spring', 'Summer', 'Fall']
    if term not in valid_terms:
        messagebox.showerror("Validation Error", f"Invalid term. Must be one of: {', '.join(valid_terms)}.")
        return
    if not str(enrollment_count).isdigit() or int(enrollment_count) < 0:
        messagebox.showerror("Validation Error", "Enrollment count must be a non-negative integer.")
        return
    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish database connection")
        cursor = conn.cursor()

        # Validate year is a four-digit number
        if not year.isdigit() or len(year) != 4:
            raise ValueError("Year must be a valid 4-digit number.")

        # Validate term is one of the allowed values
        valid_terms = ['Spring', 'Summer', 'Fall']
        if term not in valid_terms:
            raise ValueError(f"Invalid term. Must be one of: {', '.join(valid_terms)}.")

        # Validate enrollment_count is a non-negative integer
        if not str(enrollment_count).isdigit() or int(enrollment_count) < 0:
            raise ValueError("Enrollment count must be a non-negative integer.")

        # Check if the course exists
        cursor.execute("SELECT 1 FROM Course WHERE courseNumber = %s", (course_number,))
        if cursor.fetchone() is None:
            messagebox.showerror("Validation Error", f"No matching Course Number found: {course_number}")
            return

        # Check if the instructor exists
        cursor.execute("SELECT 1 FROM Instructor WHERE instructorID = %s", (instructor_id,))
        if cursor.fetchone() is None:
            messagebox.showerror("Validation Error", f"No matching Instructor ID found: {instructor_id}")
            return

        # Ensure semester exists or create it
        cursor.execute("""
            INSERT IGNORE INTO Semester (year, term) 
            VALUES (%s, %s)
        """, (year, term))

        # Add section
        cursor.execute("""
            INSERT INTO Section 
            (courseNumber, sectionID, year, term, instructorID, enrollmentCount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (course_number, section_id, year, term, instructor_id, enrollment_count))

        conn.commit()   
        cursor.execute("""
            SELECT cd.degreeID, g.goalCode
            FROM Course_Degree cd
            JOIN Goal g ON cd.degreeID = g.degreeID
            WHERE cd.courseNumber = %s
        """, (course_number,))
        degree_goals = cursor.fetchall()

        # For each degree-goal pair, insert an Evaluation record if not already existing
        for (deg_id, goal_code) in degree_goals:
            cursor.execute("""
                INSERT IGNORE INTO Evaluation (courseNumber, sectionID, year, term, degreeID, goalCode, gradeCountA, gradeCountB, gradeCountC, gradeCountF)
                VALUES (%s, %s, %s, %s, %s, %s, 0,0,0,0)
            """, (course_number, section_id, year, term, deg_id, goal_code))
        conn.commit()
        messagebox.showinfo("Success", "Course section added to semester successfully.")
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to add course to semester: {str(e)}")
    finally:
        if conn:
            conn.close()


def get_available_courses_for_semester(year, term):
    """
    Get a list of available courses for a specific semester.

    Parameters:
        year (str): The year of the semester.
        term (str): The term of the semester (e.g., Spring, Summer, Fall).

    Returns:
        List[Tuple]: A list of available courses (courseNumber, name).
    """
    # Ensure both fields are provided
    if not year.strip() or not term.strip():
        messagebox.showerror("Input Error", "Both fields (Year and Term) are required.")
        return []

    conn = None
    try:
        conn = connect_to_db()
        if not conn:
            raise ConnectionError("Failed to establish database connection.")
        cursor = conn.cursor()

        # Validate year is a four-digit number
        if not year.isdigit() or len(year) != 4:
            raise ValueError("Year must be a valid 4-digit number.")

        # Validate term is one of the allowed values
        valid_terms = ['Spring', 'Summer', 'Fall']
        if term not in valid_terms:
            raise ValueError(f"Invalid term. Must be one of: {', '.join(valid_terms)}.")

        cursor.execute("""
            SELECT DISTINCT c.courseNumber, c.name 
            FROM Course c 
            JOIN Section s ON c.courseNumber = s.courseNumber
            WHERE s.year = %s AND s.term = %s
            ORDER BY c.courseNumber
        """, (year, term))
        results = cursor.fetchall()
        return results
    except ValueError as ve:
        # Handle validation errors
        messagebox.showerror("Validation Error", f"{ve}")
        return []
    except mysql.connector.Error as e:
        # Handle database errors
        messagebox.showerror("Database Error", f"Failed to fetch available courses: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_evaluation_status_for_semester(year, term):
    """
    Retrieve the evaluation status for all sections offered in a given semester.

    Parameters:
        year (int): The academic year for which the evaluation status is retrieved (e.g., 2024).
        term (str): The term in the academic year (e.g., 'Spring', 'Summer', 'Fall').

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'courseNumber' (str): The course number (e.g., "CS101").
            - 'sectionID' (int): The section ID for the course.
            - 'status' (str): The evaluation status for the section, with possible values:
                - "No Evaluation Entered": No evaluation or grades entered for the section.
                - "Fully Entered (With Improvement Note)": Evaluation, grades, and improvement note are all entered.
                - "Fully Entered (No Improvement Note)": Evaluation and grades are entered, but no improvement note is present.
                - "Partially Entered": Either evaluation or grades are partially entered.
    """
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT s.courseNumber, s.sectionID, s.year, s.term,
           e.evaluationType, e.gradeCountA, e.gradeCountB, e.gradeCountC, e.gradeCountF, e.improvementNote
    FROM Section s
    LEFT JOIN Evaluation e 
      ON s.courseNumber = e.courseNumber 
     AND s.sectionID = e.sectionID 
     AND s.year = e.year 
     AND s.term = e.term
    WHERE s.year = %s AND s.term = %s
    ORDER BY s.courseNumber, s.sectionID;
    """
    cursor.execute(query, (year, term))
    rows = cursor.fetchall()
    conn.close()
    section_info = {}
    for row in rows:
        key = (row['courseNumber'], row['sectionID'])
        if key not in section_info:
            section_info[key] = {
                'hasEvaluation': False,
                'hasGrades': False,
                'hasImprovement': False
            }
        if row['evaluationType'] is not None or row['gradeCountA'] is not None:
            section_info[key]['hasEvaluation'] = True
        grades_sum = ((row['gradeCountA'] or 0) + (row['gradeCountB'] or 0) + (row['gradeCountC'] or 0) + (row['gradeCountF'] or 0))
        if grades_sum > 0:
            section_info[key]['hasGrades'] = True
        if row['improvementNote'] and row['improvementNote'].strip():
            section_info[key]['hasImprovement'] = True
    results = []
    for (courseNumber, sectionID), info in section_info.items():
        if not info['hasEvaluation'] and not info['hasGrades']:
            status = "No Evaluation Entered"
        else:
            if info['hasEvaluation'] and info['hasGrades']:
                if info['hasImprovement']:
                    status = "Fully Entered (With Improvement Note)"
                else:
                    status = "Fully Entered (No Improvement Note)"
            else:
                status = "Partially Entered"
        results.append({
            'courseNumber': courseNumber,
            'sectionID': sectionID,
            'status': status
        })
    return results

def get_sections_above_percentage(year, term, percentage):
    """
    Retrieve sections where the percentage of passing students exceeds a given threshold.

    Parameters:
        year (int): The academic year for which sections are retrieved (e.g., 2024).
        term (str): The term in the academic year (e.g., 'Spring', 'Summer', 'Fall').
        percentage (float): The minimum percentage of passing students to include the section.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'courseNumber' (str): The course number.
            - 'sectionID' (int): The section ID for the course.
            - 'enrollmentCount' (int): The total number of students enrolled in the section.
            - 'passCount' (int): The total number of students who passed the section.
    """
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT s.courseNumber, s.sectionID, s.enrollmentCount,
           (e.gradeCountA + e.gradeCountB + e.gradeCountC) as passCount
    FROM Section s
    JOIN Evaluation e 
      ON s.courseNumber = e.courseNumber
     AND s.sectionID = e.sectionID
     AND s.year = e.year
     AND s.term = e.term
    WHERE s.year = %s AND s.term = %s;
    """
    cursor.execute(query, (year, term))
    results = []
    for row in cursor.fetchall():
        if row['enrollmentCount'] > 0:
            ratio = (row['passCount'] / row['enrollmentCount']) * 100
            if ratio >= percentage:
                results.append(row)
    conn.close()
    return results

def get_sections_for_instructor(year, term, instructor_id):
    """
    Retrieve sections taught by a specific instructor in a given semester.

    Parameters:
        year (int): The academic year for which sections are retrieved (e.g., 2024).
        term (str): The term in the academic year (e.g., 'Spring', 'Summer', 'Fall').
        instructor_id (int): The unique ID of the instructor.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'courseNumber' (str): The course number.
            - 'sectionID' (int): The section ID for the course.
            - 'enrollmentCount' (int): The total number of students enrolled in the section.
    """
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT s.courseNumber, s.sectionID, s.enrollmentCount
    FROM Section s
    WHERE s.year = %s AND s.term = %s AND s.instructorID = %s;
    """
    cursor.execute(query, (year, term, instructor_id))
    sections = cursor.fetchall()
    conn.close()
    return sections

def get_evaluations_for_section(courseNumber, sectionID, year, term):
    """
    Retrieve evaluation details for a specific section, including associated goals and degrees.

    Parameters:
        courseNumber (str): The unique identifier for the course (e.g., "CS101").
        sectionID (int): The unique identifier for the section.
        year (int): The academic year for the section (e.g., 2024).
        term (str): The term in the academic year (e.g., 'Spring', 'Summer', 'Fall').

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - Evaluation details (e.g., 'evaluationType', 'gradeCountA', 'gradeCountB', etc.).
            - 'goalDescription' (str): Description of the goal being evaluated.
            - 'degreeName' (str): Name of the associated degree.
    """
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT e.*, g.description as goalDescription, d.name as degreeName
    FROM Evaluation e
    JOIN Goal g ON e.degreeID = g.degreeID AND e.goalCode = g.goalCode
    JOIN Degree d ON e.degreeID = d.degreeID
    WHERE e.courseNumber = %s AND e.sectionID = %s AND e.year = %s AND e.term = %s;
    """
    cursor.execute(query, (courseNumber, sectionID, year, term))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_degrees_for_course(courseNumber):
    """
    Retrieve the degree programs associated with a given course.

    Parameters:
        courseNumber (str): The unique identifier for the course (e.g., "CS101").

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'degreeID' (str): The unique identifier for the degree program.
            - 'name' (str): The name of the degree program.
            - 'isCore' (bool): Indicates whether the course is a core requirement for the degree.
    """
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT d.degreeID, d.name, cd.isCore
    FROM Course_Degree cd
    JOIN Degree d ON cd.degreeID = d.degreeID
    WHERE cd.courseNumber = %s;
    """
    cursor.execute(query, (courseNumber,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_evaluation(courseNumber, sectionID, year, term, degreeID, goalCode, evaluationType, gradeA, gradeB, gradeC, gradeF, improvementNote):
    """
    Update or insert evaluation details for a specific course section and goal.

    Parameters:
        courseNumber (str): The unique identifier for the course (e.g., "CS101").
        sectionID (int): The unique identifier for the section.
        year (int): The academic year for the section (e.g., 2024).
        term (str): The term in the academic year (e.g., 'Spring', 'Summer', 'Fall').
        degreeID (str): The unique identifier for the degree program.
        goalCode (str): The unique code for the goal being evaluated.
        evaluationType (str): The type of evaluation (e.g., "Homework", "Quiz").
        gradeA (int): The number of students achieving grade A.
        gradeB (int): The number of students achieving grade B.
        gradeC (int): The number of students achieving grade C.
        gradeF (int): The number of students achieving grade F.
        improvementNote (str): A note for improvement, if any.

    Returns:
        None
    """
    conn = connect_to_db()
    if not conn:
        return
    cursor = conn.cursor()
    query = """
    INSERT INTO Evaluation (courseNumber, sectionID, year, term, degreeID, goalCode, evaluationType, gradeCountA, gradeCountB, gradeCountC, gradeCountF, improvementNote)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
      evaluationType=VALUES(evaluationType),
      gradeCountA=VALUES(gradeCountA),
      gradeCountB=VALUES(gradeCountB),
      gradeCountC=VALUES(gradeCountC),
      gradeCountF=VALUES(gradeCountF),
      improvementNote=VALUES(improvementNote);
    """
    cursor.execute(query, (courseNumber, sectionID, year, term, degreeID, goalCode, evaluationType, gradeA, gradeB, gradeC, gradeF, improvementNote))
    conn.commit()
    conn.close()

def get_degree_courses(degreeID):
     """
    Retrieve the courses associated with a given degree program.

    Parameters:
        degreeID (str): The unique identifier for the degree program.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'courseNumber' (str): The unique identifier for the course.
            - 'name' (str): The name of the course.
            - 'isCore' (bool): Indicates whether the course is a core requirement for the degree.
    """
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT c.courseNumber, c.name, cd.isCore
    FROM Course_Degree cd
    JOIN Course c ON cd.courseNumber = c.courseNumber
    WHERE cd.degreeID = %s;
    """
    cursor.execute(query, (degreeID,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_degree_goals(degreeID):
     """
    Retrieve the goals associated with a specific degree program.

    Parameters:
        degreeID (str): The unique identifier for the degree program.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'goalCode' (str): The unique code for the goal.
            - 'description' (str): The description of the goal.
    """
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    query = "SELECT goalCode, description FROM Goal WHERE degreeID = %s;"
    cursor.execute(query, (degreeID,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_courses_for_goals(degreeID, goalCodes):
    """
    Retrieve the courses associated with specific goals for a degree program.

    Parameters:
        degreeID (str): The unique identifier for the degree program.
        goalCodes (list): A list of goal codes to filter the courses.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - 'courseNumber' (str): The unique identifier for the course.
            - 'name' (str): The name of the course.
            - 'goalCode' (str): The unique code for the goal associated with the course.
    """
    conn = connect_to_db()
    if not conn or not goalCodes:
        return []
    cursor = conn.cursor(dictionary=True)
    format_str = ','.join(['%s'] * len(goalCodes))
    query = f"""
    SELECT DISTINCT c.courseNumber, c.name, g.goalCode
    FROM Evaluation e
    JOIN Course c ON e.courseNumber = c.courseNumber
    JOIN Goal g ON e.degreeID = g.degreeID AND e.goalCode = g.goalCode
    WHERE e.degreeID = %s AND g.goalCode IN ({format_str});
    """
    params = [degreeID] + goalCodes
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_course_sections_in_range(courseNumber, startYear, startTerm, endYear, endTerm):
     """
    Retrieve course sections offered within a specific time range.

    Parameters:
        courseNumber (str): The unique identifier for the course).
        startYear (int): The starting year of the range.
        startTerm (str): The starting term of the range ('Spring', 'Summer', 'Fall').
        endYear (int): The ending year of the range.
        endTerm (str): The ending term of the range ('Spring', 'Summer', 'Fall').

    Returns:
        list: A list of dictionaries, where each dictionary represents a course section and contains all attributes of the Section table.
    """
    term_order = {'Spring': 1, 'Summer': 2, 'Fall': 3}
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT * FROM Section
    WHERE courseNumber = %s
    ORDER BY year, term
    """, (courseNumber,))
    rows = cursor.fetchall()
    def term_key(y, t):
        return y * 10 + term_order[t]
    start_val = term_key(int(startYear), startTerm)
    end_val = term_key(int(endYear), endTerm)
    filtered = []
    for r in rows:
        val = term_key(r['year'], r['term'])
        if start_val <= val <= end_val:
            filtered.append(r)
    conn.close()
    return filtered

def get_instructor_sections_in_range(instructorID, startYear, startTerm, endYear, endTerm):
    term_order = {'Spring': 1, 'Summer': 2, 'Fall': 3}
    conn = connect_to_db()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
    SELECT * FROM Section
    WHERE instructorID = %s
    ORDER BY year, term
    """, (instructorID,))
    rows = cursor.fetchall()
    def term_key(y, t):
        return y * 10 + term_order[t]
    start_val = term_key(int(startYear), startTerm)
    end_val = term_key(int(endYear), endTerm)
    filtered = []
    for r in rows:
        val = term_key(r['year'], r['term'])
        if start_val <= val <= end_val:
            filtered.append(r)
    conn.close()
    return filtered

def gui():
    root = tk.Tk()
    root.title("University Database")

    # We will use a helper function to configure centering for frames
    def configure_centering(frame):
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(3, weight=1)

    tabs = ttk.Notebook(root)

    pad_y = 1
    pad_x = 5

    degree_tab = ttk.Frame(tabs)
    tabs.add(degree_tab, text="Add Degree")
    configure_centering(degree_tab)

    ttk.Label(degree_tab, text="Degree ID:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    degree_id_entry = ttk.Entry(degree_tab)
    degree_id_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(degree_tab, text="Name:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    degree_name_entry = ttk.Entry(degree_tab)
    degree_name_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(degree_tab, text="Level:").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    degree_level_entry = ttk.Entry(degree_tab)
    degree_level_entry.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_degree():
        add_degree(degree_id_entry.get(), degree_name_entry.get(), degree_level_entry.get())

    ttk.Button(degree_tab, text="Add Degree", command=handle_add_degree).grid(row=3, column=1, columnspan=2, pady=10)

    course_tab = ttk.Frame(tabs)
    tabs.add(course_tab, text="Add Course")
    configure_centering(course_tab)

    ttk.Label(course_tab, text="Course Number:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_number_entry = ttk.Entry(course_tab)
    course_number_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(course_tab, text="Course Name:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_name_entry = ttk.Entry(course_tab)
    course_name_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_course():
        add_course(course_number_entry.get(), course_name_entry.get())

    ttk.Button(course_tab, text="Add Course", command=handle_add_course).grid(row=2, column=1, columnspan=2, pady=10)

    # Instructor Tab
    instructor_tab = ttk.Frame(tabs)
    tabs.add(instructor_tab, text="Add Instructor")
    configure_centering(instructor_tab)

    ttk.Label(instructor_tab, text="Instructor ID:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    instructor_id_entry = ttk.Entry(instructor_tab)
    instructor_id_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(instructor_tab, text="Instructor Name:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    instructor_name_entry = ttk.Entry(instructor_tab)
    instructor_name_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_instructor():
        add_instructor(instructor_id_entry.get(), instructor_name_entry.get())

    ttk.Button(instructor_tab, text="Add Instructor", command=handle_add_instructor).grid(row=2, column=1, columnspan=2, pady=10)

    # Goal Tab
    goal_tab = ttk.Frame(tabs)
    tabs.add(goal_tab, text="Add Goal")
    configure_centering(goal_tab)

    ttk.Label(goal_tab, text="Goal Code:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    goal_code_entry = ttk.Entry(goal_tab)
    goal_code_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(goal_tab, text="Degree ID:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    goal_degree_id_entry = ttk.Entry(goal_tab)
    goal_degree_id_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(goal_tab, text="Description:").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    goal_description_entry = ttk.Entry(goal_tab)
    goal_description_entry.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_goal():
        add_goal(goal_code_entry.get(), goal_degree_id_entry.get(), goal_description_entry.get())

    ttk.Button(goal_tab, text="Add Goal", command=handle_add_goal).grid(row=3, column=1, columnspan=2, pady=10)

    # Semester Tab
    semester_tab = ttk.Frame(tabs)
    tabs.add(semester_tab, text="Add Semester")
    configure_centering(semester_tab)

    ttk.Label(semester_tab, text="Year:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_year_entry = ttk.Entry(semester_tab)
    semester_year_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(semester_tab, text="Term:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_term_entry = ttk.Entry(semester_tab)
    semester_term_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_semester():
        add_semester(semester_year_entry.get(), semester_term_entry.get())

    ttk.Button(semester_tab, text="Add Semester", command=handle_add_semester).grid(row=2, column=1, columnspan=2, pady=10)

    # Section Tab
    section_tab = ttk.Frame(tabs)
    tabs.add(section_tab, text="Add Section")
    configure_centering(section_tab)

    ttk.Label(section_tab, text="Course Number:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    section_course_number_entry = ttk.Entry(section_tab)
    section_course_number_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(section_tab, text="Section ID:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    section_id_entry = ttk.Entry(section_tab)
    section_id_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(section_tab, text="Year:").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    section_year_entry = ttk.Entry(section_tab)
    section_year_entry.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(section_tab, text="Term:").grid(row=3, column=1, padx=pad_x, pady=pad_y, sticky='e')
    section_term_entry = ttk.Entry(section_tab)
    section_term_entry.grid(row=3, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(section_tab, text="Instructor ID:").grid(row=4, column=1, padx=pad_x, pady=pad_y, sticky='e')
    section_instructor_id_entry = ttk.Entry(section_tab)
    section_instructor_id_entry.grid(row=4, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(section_tab, text="Enrollment Count:").grid(row=5, column=1, padx=pad_x, pady=pad_y, sticky='e')
    section_enrollment_count_entry = ttk.Entry(section_tab)
    section_enrollment_count_entry.grid(row=5, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_section():
        add_section(
            section_course_number_entry.get(),
            section_id_entry.get(),
            section_year_entry.get(),
            section_term_entry.get(),
            section_instructor_id_entry.get(),
            section_enrollment_count_entry.get()
        )

    ttk.Button(section_tab, text="Add Section", command=handle_add_section).grid(row=6, column=1, columnspan=2, pady=10)

    # Course-Degree Association Tab
    course_degree_tab = ttk.Frame(tabs)
    tabs.add(course_degree_tab, text="Associate Course to Degree")
    configure_centering(course_degree_tab)

    ttk.Label(course_degree_tab, text="Course Number:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_degree_course_number_entry = ttk.Entry(course_degree_tab)
    course_degree_course_number_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(course_degree_tab, text="Degree ID:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_degree_degree_id_entry = ttk.Entry(course_degree_tab)
    course_degree_degree_id_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(course_degree_tab, text="Is Core (1=True, 0=False):").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_degree_is_core_entry = ttk.Entry(course_degree_tab)
    course_degree_is_core_entry.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_course_degree():
        add_course_degree(
            course_degree_course_number_entry.get(),
            course_degree_degree_id_entry.get(),
            int(course_degree_is_core_entry.get())
        )

    ttk.Button(course_degree_tab, text="Add Association", command=handle_add_course_degree).grid(row=3, column=1, columnspan=2, pady=10)


    # Course-Goal Association Tab
    course_goal_tab = ttk.Frame(tabs)
    tabs.add(course_goal_tab, text="Associate Course with Goal")
    configure_centering(course_goal_tab)

    ttk.Label(course_goal_tab, text="Course Number:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_goal_course_number = ttk.Entry(course_goal_tab)
    course_goal_course_number.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(course_goal_tab, text="Degree ID:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_goal_degree_id = ttk.Entry(course_goal_tab)
    course_goal_degree_id.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(course_goal_tab, text="Goal Code:").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    course_goal_code = ttk.Entry(course_goal_tab)
    course_goal_code.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_associate_course_goal():
        associate_course_with_goal(
            course_goal_course_number.get(),
            course_goal_degree_id.get(),
            course_goal_code.get()
        )

    ttk.Button(course_goal_tab, text="Associate", command=handle_associate_course_goal).grid(row=3, column=1, columnspan=2, pady=10)

    # Semester Course Entry Tab
    semester_course_tab = ttk.Frame(tabs)
    tabs.add(semester_course_tab, text="Add Course to Semester")
    configure_centering(semester_course_tab)

    ttk.Label(semester_course_tab, text="Year:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_course_year = ttk.Entry(semester_course_tab)
    semester_course_year.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(semester_course_tab, text="Term:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_course_term = ttk.Combobox(semester_course_tab, values=['Spring', 'Summer', 'Fall'])
    semester_course_term.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(semester_course_tab, text="Course Number:").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_course_number = ttk.Entry(semester_course_tab)
    semester_course_number.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(semester_course_tab, text="Section ID:").grid(row=3, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_section_id = ttk.Entry(semester_course_tab)
    semester_section_id.grid(row=3, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(semester_course_tab, text="Instructor ID:").grid(row=4, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_instructor_id = ttk.Entry(semester_course_tab)
    semester_instructor_id.grid(row=4, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(semester_course_tab, text="Enrollment Count:").grid(row=5, column=1, padx=pad_x, pady=pad_y, sticky='e')
    semester_enrollment_count = ttk.Entry(semester_course_tab)
    semester_enrollment_count.grid(row=5, column=2, padx=pad_x, pady=pad_y, sticky='w')

    def handle_add_course_to_semester():
        add_course_to_semester(
            semester_course_number.get(),
            semester_section_id.get(),
            semester_course_year.get(),
            semester_course_term.get(),
            semester_instructor_id.get(),
            semester_enrollment_count.get() or 0
        )

    ttk.Button(semester_course_tab, text="Add to Semester", command=handle_add_course_to_semester).grid(row=6, column=1, columnspan=2, pady=10)

    queries_tab = ttk.Frame(tabs)
    tabs.add(queries_tab, text="Queries & Evaluations")

    query_notebook = ttk.Notebook(queries_tab)
    query_notebook.pack(expand=1, fill="both")

     # Apply same centering to query subtabs
    eval_status_frame = ttk.Frame(query_notebook)
    query_notebook.add(eval_status_frame, text="Evaluation Status by Semester")
    configure_centering(eval_status_frame)

    ttk.Label(eval_status_frame, text="Year:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_status_year_entry = ttk.Entry(eval_status_frame)
    eval_status_year_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_status_frame, text="Term:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_status_term_entry = ttk.Entry(eval_status_frame)
    eval_status_term_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    eval_status_tree = ttk.Treeview(eval_status_frame, columns=("CourseNumber","SectionID","Status"), show='headings')
    eval_status_tree.heading("CourseNumber", text="Course Number")
    eval_status_tree.heading("SectionID", text="Section ID")
    eval_status_tree.heading("Status", text="Evaluation Status")
    eval_status_tree.grid(row=3, column=1, columnspan=2, sticky='nsew')
    eval_status_frame.grid_rowconfigure(3, weight=1)
    eval_status_frame.grid_columnconfigure(0, weight=1)
    eval_status_frame.grid_columnconfigure(3, weight=1)

    eval_status_tree.column("CourseNumber", width=120)
    eval_status_tree.column("SectionID", width=80)
    eval_status_tree.column("Status", width=300)

    def handle_eval_status_query():
        for i in eval_status_tree.get_children():
            eval_status_tree.delete(i)
        year = eval_status_year_entry.get()
        term = eval_status_term_entry.get()
        results = get_evaluation_status_for_semester(year, term)
        for r in results:
            eval_status_tree.insert('', 'end', values=(r['courseNumber'], r['sectionID'], r['status']))

    ttk.Button(eval_status_frame, text="Get Evaluation Status", command=handle_eval_status_query).grid(row=2, column=1, columnspan=2, pady=10)

    percentage_frame = ttk.Frame(query_notebook)
    query_notebook.add(percentage_frame, text="Sections Above Percentage")
    configure_centering(percentage_frame)

    ttk.Label(percentage_frame, text="Year:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    pct_year_entry = ttk.Entry(percentage_frame)
    pct_year_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(percentage_frame, text="Term:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    pct_term_entry = ttk.Entry(percentage_frame)
    pct_term_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(percentage_frame, text="Percentage:").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    pct_entry = ttk.Entry(percentage_frame)
    pct_entry.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    pct_tree = ttk.Treeview(percentage_frame, columns=("CourseNumber","SectionID","EnrollmentCount","PassCount"), show='headings')
    pct_tree.heading("CourseNumber", text="Course Number")
    pct_tree.heading("SectionID", text="Section ID")
    pct_tree.heading("EnrollmentCount", text="Enrollment")
    pct_tree.heading("PassCount", text="A+B+C Count")
    pct_tree.grid(row=4, column=1, columnspan=2, sticky='nsew')
    percentage_frame.grid_rowconfigure(4, weight=1)
    percentage_frame.grid_columnconfigure(0, weight=1)
    percentage_frame.grid_columnconfigure(3, weight=1)

    pct_tree.column("CourseNumber", width=120)
    pct_tree.column("SectionID", width=80)
    pct_tree.column("EnrollmentCount", width=100)
    pct_tree.column("PassCount", width=100)

    def handle_pct_query():
        for i in pct_tree.get_children():
            pct_tree.delete(i)
        year = pct_year_entry.get()
        term = pct_term_entry.get()
        percentage = float(pct_entry.get())
        results = get_sections_above_percentage(year, term, percentage)
        for r in results:
            pct_tree.insert('', 'end', values=(r['courseNumber'], r['sectionID'], r['enrollmentCount'], r['passCount']))

    ttk.Button(percentage_frame, text="Get Sections", command=handle_pct_query).grid(row=3, column=1, columnspan=2, pady=10)

    eval_entry_frame = ttk.Frame(query_notebook)
    query_notebook.add(eval_entry_frame, text="Enter/Update Evaluations")
    configure_centering(eval_entry_frame)

    ttk.Label(eval_entry_frame, text="Year:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_ent_year = ttk.Entry(eval_entry_frame)
    eval_ent_year.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Term:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_ent_term = ttk.Entry(eval_entry_frame)
    eval_ent_term.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Instructor ID:").grid(row=2, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_ent_instructor = ttk.Entry(eval_entry_frame)
    eval_ent_instructor.grid(row=2, column=2, padx=pad_x, pady=pad_y, sticky='w')

    # Status column
    eval_sections_tree = ttk.Treeview(eval_entry_frame, columns=("CourseNumber","SectionID","Enrollment","Status"), show='headings')
    eval_sections_tree.heading("CourseNumber", text="Course Number")
    eval_sections_tree.heading("SectionID", text="Section ID")
    eval_sections_tree.heading("Enrollment", text="Enrollment")
    eval_sections_tree.heading("Status", text="Status")
    eval_sections_tree.grid(row=4, column=1, columnspan=2, sticky='nsew')
    eval_entry_frame.grid_rowconfigure(4, weight=1)
    eval_entry_frame.grid_columnconfigure(0, weight=1)
    eval_entry_frame.grid_columnconfigure(3, weight=1)

    eval_sections_tree.column("CourseNumber", width=120)
    eval_sections_tree.column("SectionID", width=80)
    eval_sections_tree.column("Enrollment", width=100)
    eval_sections_tree.column("Status", width=300)

    def handle_list_instructor_sections():
        for i in eval_sections_tree.get_children():
            eval_sections_tree.delete(i)
        year = eval_ent_year.get()
        term = eval_ent_term.get()
        instr = eval_ent_instructor.get()
        sections = get_sections_for_instructor(year, term, instr)

        # Get the evaluation status for this semester
        all_status = get_evaluation_status_for_semester(year, term)
        status_map = {(x['courseNumber'], x['sectionID']): x['status'] for x in all_status}

        for s in sections:
            sec_status = status_map.get((s['courseNumber'], s['sectionID']), "No Evaluation Entered")
            eval_sections_tree.insert('', 'end', values=(s['courseNumber'], s['sectionID'], s['enrollmentCount'], sec_status))

    ttk.Button(eval_entry_frame, text="List Sections", command=handle_list_instructor_sections).grid(row=3, column=1, columnspan=2, pady=10)

    ttk.Label(eval_entry_frame, text="Select Section and Enter New/Update Evaluations Below:").grid(row=5, column=1, columnspan=2)

    ttk.Label(eval_entry_frame, text="DegreeID:").grid(row=6, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_deg_id = ttk.Entry(eval_entry_frame)
    eval_deg_id.grid(row=6, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="GoalCode:").grid(row=7, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_goal_code = ttk.Entry(eval_entry_frame)
    eval_goal_code.grid(row=7, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Eval Type:").grid(row=8, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_type = ttk.Entry(eval_entry_frame)
    eval_type.grid(row=8, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Grade A:").grid(row=9, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_A = ttk.Entry(eval_entry_frame)
    eval_A.grid(row=9, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Grade B:").grid(row=10, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_B = ttk.Entry(eval_entry_frame)
    eval_B.grid(row=10, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Grade C:").grid(row=11, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_C = ttk.Entry(eval_entry_frame)
    eval_C.grid(row=11, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Grade F:").grid(row=12, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_F = ttk.Entry(eval_entry_frame)
    eval_F.grid(row=12, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(eval_entry_frame, text="Improvement Note:").grid(row=13, column=1, padx=pad_x, pady=pad_y, sticky='e')
    eval_improve = ttk.Entry(eval_entry_frame)
    eval_improve.grid(row=13, column=2, padx=pad_x, pady=pad_y, sticky='w')

    # ADD the on_section_selected function from user's code
    def on_section_selected():
        sel = eval_sections_tree.selection()
        if not sel:
            return
        vals = eval_sections_tree.item(sel[0], 'values')
        courseNumber, sectionID, enrollmentCount_str, currentStatus = vals
        year = eval_ent_year.get()
        term = eval_ent_term.get()

        evaluations = get_evaluations_for_section(courseNumber, sectionID, year, term)

        # Clear fields first
        eval_deg_id.delete(0, tk.END)
        eval_goal_code.delete(0, tk.END)
        eval_type.delete(0, tk.END)
        eval_A.delete(0, tk.END)
        eval_B.delete(0, tk.END)
        eval_C.delete(0, tk.END)
        eval_F.delete(0, tk.END)
        eval_improve.delete(0, tk.END)

        if not evaluations:
            # No evaluation entered yet
            return

        # Take the first evaluation record as an example
        eval_data = evaluations[0]
        eval_deg_id.insert(0, eval_data['degreeID'])
        eval_goal_code.insert(0, eval_data['goalCode'])
        if eval_data['evaluationType'] is not None:
            eval_type.insert(0, eval_data['evaluationType'])

        eval_A.insert(0, eval_data['gradeCountA'] if eval_data['gradeCountA'] is not None else 0)
        eval_B.insert(0, eval_data['gradeCountB'] if eval_data['gradeCountB'] is not None else 0)
        eval_C.insert(0, eval_data['gradeCountC'] if eval_data['gradeCountC'] is not None else 0)
        eval_F.insert(0, eval_data['gradeCountF'] if eval_data['gradeCountF'] is not None else 0)
        if eval_data['improvementNote'] is not None:
            eval_improve.insert(0, eval_data['improvementNote'])

    eval_sections_tree.bind("<<TreeviewSelect>>", lambda e: on_section_selected())

    # Use the handle_update_evaluation logic from user's code
    def handle_update_evaluation():
        sel = eval_sections_tree.selection()
        if not sel:
            messagebox.showerror("Error", "No section selected.")
            return
        vals = eval_sections_tree.item(sel[0], 'values')
        # vals = (courseNumber, sectionID, enrollmentCount, status)
        courseNumber, sectionID, enrollmentCount_str, currentStatus = vals
        enrollmentCount = int(enrollmentCount_str)
        year = eval_ent_year.get()
        term = eval_ent_term.get()
        degreeID = eval_deg_id.get()
        goalCode = eval_goal_code.get()
        evaluationType = eval_type.get()
        gradeA = int(eval_A.get() or 0)
        gradeB = int(eval_B.get() or 0)
        gradeC = int(eval_C.get() or 0)
        gradeF = int(eval_F.get() or 0)
        improvementNote = eval_improve.get()

        # Ensure A+B+C+F = enrollmentCount
        total_grades = gradeA + gradeB + gradeC + gradeF
        if total_grades != enrollmentCount:
            messagebox.showerror("Validation Error", "The sum of A, B, C, and F grades must equal the enrollment count.")
            return

        # Update the evaluation for this degree
        update_evaluation(courseNumber, sectionID, year, term, degreeID, goalCode, evaluationType, gradeA, gradeB, gradeC, gradeF, improvementNote)
        messagebox.showinfo("Success", "Evaluation updated.")

        # Duplication for other degrees
        degrees = get_degrees_for_course(courseNumber)
        other_degrees = [d for d in degrees if d['degreeID'] != degreeID]

        if other_degrees:
            ans = messagebox.askyesno("Duplicate Evaluation", "This course is associated with other degrees. Duplicate this evaluation?")
            if ans:
                for d in other_degrees:
                    update_evaluation(courseNumber, sectionID, year, term, d['degreeID'], goalCode, evaluationType, gradeA, gradeB, gradeC, gradeF, improvementNote)
                messagebox.showinfo("Success", "Evaluation duplicated across all associated degrees.")

        # Refresh the status of this row in the treeview
        all_status = get_evaluation_status_for_semester(year, term)
        status_map = {(x['courseNumber'], x['sectionID']): x['status'] for x in all_status}
        new_status = status_map.get((courseNumber, sectionID), "No Evaluation Entered")
        eval_sections_tree.item(sel[0], values=(courseNumber, sectionID, enrollmentCount, new_status))

    ttk.Button(eval_entry_frame, text="Update Evaluation", command=handle_update_evaluation).grid(row=14, column=1, columnspan=2, pady=10)

    additional_queries_frame = ttk.Frame(query_notebook)
    query_notebook.add(additional_queries_frame, text="Additional Queries")
    configure_centering(additional_queries_frame)

    ttk.Label(additional_queries_frame, text="Degree ID:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    aq_degree_entry = ttk.Entry(additional_queries_frame)
    aq_degree_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    aq_courses_tree = ttk.Treeview(additional_queries_frame, columns=("CourseNumber","Name","IsCore"), show='headings')
    aq_courses_tree.heading("CourseNumber", text="Course Number")
    aq_courses_tree.heading("Name", text="Name")
    aq_courses_tree.heading("IsCore", text="Is Core")
    aq_courses_tree.grid(row=2, column=1, columnspan=2, sticky='nsew')
    additional_queries_frame.grid_rowconfigure(2, weight=1)
    additional_queries_frame.grid_columnconfigure(0, weight=1)
    additional_queries_frame.grid_columnconfigure(3, weight=1)

    def handle_degree_courses_query():
        for i in aq_courses_tree.get_children():
            aq_courses_tree.delete(i)
        degID = aq_degree_entry.get()
        rows = get_degree_courses(degID)
        for r in rows:
            aq_courses_tree.insert('', 'end', values=(r['courseNumber'], r['name'], r['isCore']))

    ttk.Button(additional_queries_frame, text="List Degree Courses", command=handle_degree_courses_query).grid(row=1, column=1, columnspan=2, pady=10)

    show_note_frame = ttk.Frame(query_notebook)
    query_notebook.add(show_note_frame, text="Show Improvement Note")
    configure_centering(show_note_frame)

    ttk.Label(show_note_frame, text="Course Number:").grid(row=0, column=1, padx=pad_x, pady=pad_y, sticky='e')
    show_note_course_entry = ttk.Entry(show_note_frame)
    show_note_course_entry.grid(row=0, column=2, padx=pad_x, pady=pad_y, sticky='w')

    ttk.Label(show_note_frame, text="Section ID:").grid(row=1, column=1, padx=pad_x, pady=pad_y, sticky='e')
    show_note_section_entry = ttk.Entry(show_note_frame)
    show_note_section_entry.grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky='w')

    notes_text = tk.Text(show_note_frame, width=50, height=10)
    notes_text.grid(row=3, column=1, columnspan=2, sticky='nsew')
    show_note_frame.grid_rowconfigure(3, weight=1)
    show_note_frame.grid_columnconfigure(0, weight=1)
    show_note_frame.grid_columnconfigure(3, weight=1)

    def show_improvement_note():
        # Enable editing to clear previous notes
        notes_text.config(state='normal')
        notes_text.delete('1.0', tk.END)

        course_num = show_note_course_entry.get().strip()
        section_id = show_note_section_entry.get().strip()

        if not course_num or not section_id:
            messagebox.showerror("Input Error", "Course Number and Section ID are required.")
            # Disable again after message
            notes_text.config(state='disabled')
            return

        conn = connect_to_db()
        if not conn:
            notes_text.config(state='disabled')
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.degreeID, d.name as degreeName, e.improvementNote
            FROM Evaluation e
            JOIN Degree d ON e.degreeID = d.degreeID
            WHERE e.courseNumber = %s AND e.sectionID = %s AND e.improvementNote IS NOT NULL AND e.improvementNote <> ''
        """, (course_num, section_id))
        notes = cursor.fetchall()
        conn.close()

        if not notes:
            notes_text.insert(tk.END, "No improvement notes found for this section.")
        else:
            for n in notes:
                notes_text.insert(tk.END, f"Degree: {n['degreeID']} ({n['degreeName']})\nNote: {n['improvementNote']}\n---\n")

        # Disable editing after inserting the notes
        notes_text.config(state='disabled')

    ttk.Button(show_note_frame, text="Show Improvement Note", command=show_improvement_note).grid(row=2, column=1, columnspan=2, pady=10)

    tabs.pack(expand=1, fill="both")
    root.mainloop()
        
# Main section
if __name__ == "__main__":
    # Initialize database first
    initial_conn = connect_to_db()
    if initial_conn:
        initial_conn.close()
        # Start GUI
        gui()
    else:
        print("Failed to initialize database. Please check your MySQL connection.")
