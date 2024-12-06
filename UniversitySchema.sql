DROP DATABASE IF EXISTS university;
CREATE DATABASE university;
USE university;

-- First, drop all tables in the correct order
DROP TABLE IF EXISTS Evaluation;
DROP TABLE IF EXISTS Section;
DROP TABLE IF EXISTS Goal;
DROP TABLE IF EXISTS Course_Degree;
DROP TABLE IF EXISTS Course;
DROP TABLE IF EXISTS Instructor;
DROP TABLE IF EXISTS Degree;
DROP TABLE IF EXISTS Semester;

-- Create base tables first
CREATE TABLE Degree (
    degreeID VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    level VARCHAR(50) NOT NULL
);

CREATE TABLE Course (
    courseNumber VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Semester (
    year INT NOT NULL,
    term ENUM('Spring', 'Summer', 'Fall') NOT NULL,
    PRIMARY KEY (year, term)
);

CREATE TABLE Instructor (
    instructorID VARCHAR(8) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE Course_Degree (
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

CREATE TABLE Goal (
    goalCode VARCHAR(4),
    degreeID VARCHAR(10),
    description TEXT NOT NULL,
    PRIMARY KEY (goalCode, degreeID),
    UNIQUE KEY goal_degree_idx (degreeID, goalCode),  -- Added UNIQUE constraint for foreign key reference
    FOREIGN KEY (degreeID) 
        REFERENCES Degree(degreeID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Section (
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

CREATE TABLE Evaluation (
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