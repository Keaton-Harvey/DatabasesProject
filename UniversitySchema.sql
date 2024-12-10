CREATE DATABASE IF NOT EXISTS university;
USE university;

-- Create base tables first
CREATE TABLE IF NOT EXISTS Degree (
    degreeID VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    level VARCHAR(10) NOT NULL,  -- Changed from ENUM to VARCHAR(10)
    CONSTRAINT unique_name_level UNIQUE (name, level),  -- Named constraint for uniqueness
    CONSTRAINT valid_level CHECK (level IN ('BA', 'BS', 'MS', 'Ph.D.', 'Cert')) 
);

CREATE TABLE IF NOT EXISTS Course (
    courseNumber VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Semester (
    year INT NOT NULL,
    term ENUM('Spring', 'Summer', 'Fall') NOT NULL,
    PRIMARY KEY (year, term)
);

CREATE TABLE IF NOT EXISTS Instructor (
    instructorID VARCHAR(8) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Course_Degree (
    degreeID VARCHAR(10),
    courseNumber VARCHAR(50),
    isCore BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (degreeID, courseNumber),
    FOREIGN KEY (degreeID) 
        REFERENCES Degree(degreeID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (courseNumber) 
        REFERENCES Course(courseNumber)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Goal (
    goalCode VARCHAR(4),
    degreeID VARCHAR(10),
    description TEXT NOT NULL,
    PRIMARY KEY (goalCode, degreeID),
    UNIQUE KEY goal_degree_idx (degreeID, goalCode),
    FOREIGN KEY (degreeID) 
        REFERENCES Degree(degreeID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Section (
    courseNumber VARCHAR(50),
    sectionID VARCHAR(3),
    year INT,
    term ENUM('Spring', 'Summer', 'Fall'),
    instructorID VARCHAR(8),
    enrollmentCount INT NOT NULL DEFAULT 0,
    PRIMARY KEY (courseNumber, sectionID, year, term),
    FOREIGN KEY (courseNumber) 
        REFERENCES Course(courseNumber)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (instructorID) 
        REFERENCES Instructor(instructorID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (year, term) 
        REFERENCES Semester(year, term)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (enrollmentCount >= 0)
);

CREATE TABLE IF NOT EXISTS Evaluation (
    courseNumber VARCHAR(50),
    sectionID VARCHAR(3),
    year INT,
    term ENUM('Spring', 'Summer', 'Fall'),
    degreeID VARCHAR(10),
    goalCode VARCHAR(4),
    evaluationType ENUM('Homework', 'Project', 'Quiz', 'Oral Presentation', 'Report', 'Mid-term', 'Final Exam', 'Other'),
    gradeCountA INT NOT NULL DEFAULT 0,
    gradeCountB INT NOT NULL DEFAULT 0,
    gradeCountC INT NOT NULL DEFAULT 0,
    gradeCountF INT NOT NULL DEFAULT 0,
    improvementNote TEXT,
    PRIMARY KEY (courseNumber, sectionID, year, term, degreeID, goalCode),
    FOREIGN KEY (courseNumber, sectionID, year, term) 
        REFERENCES Section(courseNumber, sectionID, year, term)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (degreeID, goalCode) 
        REFERENCES Goal(degreeID, goalCode)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (gradeCountA >= 0 AND gradeCountB >= 0 AND gradeCountC >= 0 AND gradeCountF >= 0)
);
