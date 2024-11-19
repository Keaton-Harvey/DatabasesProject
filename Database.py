import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# Database connection
def connect_to_db():
    return mysql.connector.connect(
        user="cs5330",
        password="pw5330",
        database="DatabasesProject"
    )

# Queries:

def get_courses_by_degree(degree_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT C.courseNumber, C.name, DC.isCore
        FROM Degree_Course DC
        JOIN Course C ON DC.courseNumber = C.courseNumber
        WHERE DC.degreeID = %s;
    """, (degree_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_sections_by_time_range(start_year, end_year):
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
    conn.close()
    return rows

def get_courses_by_goal(goal_code):
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
    conn.close()
    return rows


def get_goals_by_degree(degree_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT goalCode, description
        FROM Goal
        WHERE degreeID = %s;
    """, (degree_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_sections_by_course(course_number, start_year, end_year):
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
    conn.close()
    return rows

def get_sections_by_instructor(instructor_id, start_year, end_year):
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
    conn.close()
    return rows

def get_evaluation_status(semester_id):
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
    conn.close()
    return rows

def get_high_passing_sections(semester_id, percentage_threshold):
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
    conn.close()
    return rows

# Data Entry

# Fetch semesters
def fetch_semesters():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT semesterID, year, term FROM Semester")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fetch instructors
def fetch_instructors():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT instructorID, name FROM Instructor")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fetch sections taught by instructor in a semester
def fetch_sections(instructor_id, semester_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT S.courseNumber, S.sectionID, C.name
        FROM Section S
        JOIN Course C ON S.courseNumber = C.courseNumber
        WHERE S.instructorID = %s AND S.semesterID = %s
    """, (instructor_id, semester_id))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fetch evaluation data
def fetch_evaluations(course_number, section_id, semester_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT goalCode, evaluationType, gradeCountA, gradeCountB, gradeCountC, gradeCountF, improvementNote
        FROM Evaluation
        WHERE courseNumber = %s AND sectionID = %s AND semesterID = %s
    """, (course_number, section_id, semester_id))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Add or update evaluation
def save_evaluation(data):
    conn = connect_to_db()
    cursor = conn.cursor()
    for entry in data:
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
