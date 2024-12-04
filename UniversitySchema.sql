CREATE TABLE IF NOT EXISTS Degree (
    degreeID INT PRIMARY KEY,
    name VARCHAR(255),
    level VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Course (
    courseNumber VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Semester (
    semesterID INT PRIMARY KEY,
    year INT,
    term VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS Goal (
    goalCode VARCHAR(50),
    degreeID INT,
    description TEXT,
    PRIMARY KEY (goalCode, degreeID),
    FOREIGN KEY (degreeID) REFERENCES Degree(degreeID)
);

CREATE TABLE IF NOT EXISTS Instructor (
    instructorID INT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS Section (
    courseNumber VARCHAR(50),
    sectionID INT,
    instructorID INT,
    semesterID INT,
    enrollmentCount INT,
    PRIMARY KEY (courseNumber, sectionID, semesterID),
    FOREIGN KEY (courseNumber, semesterID) REFERENCES OfferedCourse(courseNumber, semesterID),
    FOREIGN KEY (instructorID) REFERENCES Instructor(instructorID),
    FOREIGN KEY (semesterID) REFERENCES Semester(semesterID)
);

CREATE TABLE IF NOT EXISTS Degree_Course (
    degreeID INT,
    courseNumber VARCHAR(50),
    isCore BOOLEAN,
    PRIMARY KEY (degreeID, courseNumber),
    FOREIGN KEY (degreeID) REFERENCES Degree(degreeID),
    FOREIGN KEY (courseNumber) REFERENCES Course(courseNumber)
);

CREATE TABLE IF NOT EXISTS Evaluation (
    courseNumber VARCHAR(50),
    sectionID INT,
    degreeID INT,
    semesterID VARCHAR(10),
    goalCode VARCHAR(50),
    evaluationType VARCHAR(50),
    gradeCountA INT,
    gradeCountB INT,
    gradeCountC INT,
    gradeCountF INT,
    improvementNote TEXT,
    PRIMARY KEY (courseNumber, sectionID, semesterID, degreeID, goalCode),
    FOREIGN KEY (courseNumber, sectionID, semesterID) 
        REFERENCES Section(courseNumber, sectionID, semesterID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (degreeID, goalCode) 
        REFERENCES Goal(degreeID, goalCode)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT check_grade_counts 
        CHECK (gradeCountA >= 0 AND gradeCountB >= 0 AND gradeCountC >= 0 AND gradeCountF >= 0)
);
