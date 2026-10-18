-- ApplyPilot MySQL setup script.
-- Run this once in MySQL Workbench or the mysql CLI before the robot's first
-- database run. It creates the database, the applicants table, and a
-- dedicated login the robot can use instead of the root account.

CREATE DATABASE IF NOT EXISTS applypilot_db;
USE applypilot_db;

-- Email is stored already normalised (trimmed + lowercase) by the robot
-- before it ever reaches this table, so a plain UNIQUE constraint on Email
-- is enough to stop the same applicant being inserted twice.
CREATE TABLE IF NOT EXISTS applicants (
    ApplicantId       INT AUTO_INCREMENT PRIMARY KEY,
    CandidateName     VARCHAR(150) NOT NULL DEFAULT 'Not Found',
    Email             VARCHAR(190) NOT NULL,
    Phone             VARCHAR(50)  NOT NULL DEFAULT 'Not Found',
    Education         VARCHAR(150) NOT NULL DEFAULT 'Not Found',
    ExperienceYears   INT          NOT NULL DEFAULT 0,
    Skills            VARCHAR(200) NOT NULL DEFAULT 'No Technical Skills Detected',
    Score             INT          NOT NULL DEFAULT 0,
    Priority          VARCHAR(10)  NOT NULL DEFAULT 'Low',
    ResumeFileName    VARCHAR(255) NOT NULL,
    ApplicationStatus VARCHAR(20)  NOT NULL DEFAULT 'Processed',
    ProcessedDate     DATETIME     NOT NULL,
    CONSTRAINT uq_applicants_email UNIQUE (Email)
);

-- Optional but recommended: a dedicated account for the robot instead of
-- using root. Change the password before running this, and use that same
-- password in the robot's connection string / Orchestrator credential asset,
-- never in the XAML itself.
CREATE USER IF NOT EXISTS 'applypilot_robot'@'localhost' IDENTIFIED BY 'CHANGE_THIS_PASSWORD';
GRANT SELECT, INSERT ON applypilot_db.applicants TO 'applypilot_robot'@'localhost';
FLUSH PRIVILEGES;

-- ----------------------------------------------------------------------
-- Reference queries used by CheckAndSaveApplicant.xaml (parameterized -
-- UiPath supplies the @Email etc. values as Query Parameters, never by
-- building this text with string concatenation).
-- ----------------------------------------------------------------------

-- Duplicate check: run first for every applicant.
-- SELECT COUNT(*) AS MatchCount FROM applicants WHERE Email = @Email;

-- Insert: run only when the duplicate check above returns 0.
-- INSERT INTO applicants
--     (CandidateName, Email, Phone, Education, ExperienceYears, Skills, Score, Priority, ResumeFileName, ApplicationStatus, ProcessedDate)
-- VALUES
--     (@CandidateName, @Email, @Phone, @Education, @ExperienceYears, @Skills, @Score, @Priority, @ResumeFileName, @ApplicationStatus, @ProcessedDate);
