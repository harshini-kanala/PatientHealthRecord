CREATE DATABASE PatientHealthDB;
USE PatientHealthDB;

CREATE TABLE Patient (
    PatientID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    DOB DATE,
    Gender CHAR(1),
    Phone VARCHAR(15) UNIQUE,
    Address TEXT,
    BloodGroup VARCHAR(5)
);

CREATE TABLE Doctor (
    DoctorID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Specialization VARCHAR(50),
    Phone VARCHAR(15) UNIQUE,
    Email VARCHAR(100) UNIQUE
);

CREATE TABLE Appointment (
    AppointmentID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    DoctorID INT,
    AppointmentDate DATE,
    AppointmentTime TIME,
    Status VARCHAR(20) DEFAULT 'Scheduled',
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID),
    UNIQUE(PatientID, DoctorID, AppointmentDate, AppointmentTime)
);

CREATE TABLE MedicalRecord (
    RecordID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    Diagnosis TEXT,
    Prescription TEXT,
    RecordDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
);

CREATE TABLE Billing (
    BillID INT PRIMARY KEY AUTO_INCREMENT,
    PatientID INT,
    Amount DECIMAL(10,2),
    PaymentStatus VARCHAR(20) DEFAULT 'Pending',
    BillDate DATE,
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    CHECK (PaymentStatus IN ('Pending','Paid','Cancelled'))
);

INSERT INTO Patient (Name, DOB, Gender, Phone, Address, BloodGroup)
VALUES ('Rahul Sharma','1990-05-12','M','9876543210','Delhi','O+'),
       ('Priya Mehta','1985-11-23','F','9123456789','Mumbai','A+');

INSERT INTO Doctor (Name, Specialization, Phone, Email)
VALUES ('Dr. Meena','Cardiology','9988776655','meena@hospital.com'),
       ('Dr. Arjun','Orthopedics','8877665544','arjun@hospital.com');

INSERT INTO Appointment (PatientID, DoctorID, AppointmentDate, AppointmentTime)
VALUES (1,1,'2025-09-30','10:30:00'),
       (2,2,'2025-10-01','11:00:00');

INSERT INTO MedicalRecord (PatientID, Diagnosis, Prescription, RecordDate)
VALUES (1,'High BP','Amlodipine 5mg daily','2025-09-25');

INSERT INTO Billing (PatientID, Amount, PaymentStatus, BillDate)
VALUES (1,500.00,'Pending','2025-09-25');

