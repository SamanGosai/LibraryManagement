-- Create the Library Database
CREATE DATABASE LibraryDB;
GO

-- Use the Library Database
USE LibraryDB;
GO

-- Create the Book Table
CREATE TABLE Book (
    BookID INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(255) NOT NULL,
    Author NVARCHAR(255) NOT NULL,
    ISBN NVARCHAR(13) UNIQUE NOT NULL,
    Genre NVARCHAR(100),
    PublishedYear INT,
    Status NVARCHAR(20) CHECK (Status IN ('Available', 'Checked Out'))
);

-- Create the Member Table
CREATE TABLE Member (
    MemberID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(255) NOT NULL,
    Email NVARCHAR(255) UNIQUE NOT NULL,
    Phone NVARCHAR(15),
    Address NVARCHAR(MAX),
    MembershipStartDate DATE
);

-- Create the Loan Table
CREATE TABLE Loan (
    LoanID INT IDENTITY(1,1) PRIMARY KEY,
    BookID INT FOREIGN KEY REFERENCES Book(BookID),
    MemberID INT FOREIGN KEY REFERENCES Member(MemberID),
    LoanDate DATE NOT NULL,
    DueDate DATE NOT NULL,
    ReturnDate DATE
);

-- Create the Fine Table
CREATE TABLE Fine (
    FineID INT IDENTITY(1,1) PRIMARY KEY,
    LoanID INT FOREIGN KEY REFERENCES Loan(LoanID),
    Amount DECIMAL(10, 2) NOT NULL,
    PaidStatus NVARCHAR(10) CHECK (PaidStatus IN ('Paid', 'Unpaid'))
);
-- Insert Sample Books
INSERT INTO Book (Title, Author, ISBN, Genre, PublishedYear, Status)
VALUES 
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 'Fiction', 1925, 'Available'),
('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 'Fiction', 1960, 'Available'),
('1984', 'George Orwell', '9780451524935', 'Dystopian', 1949, 'Available');

-- Insert Sample Members
INSERT INTO Member (Name, Email, Phone, Address, MembershipStartDate)
VALUES 
('John Doe', 'john.doe@example.com', '123-456-7890', '123 Main St, Cityville', '2023-01-01'),
('Jane Smith', 'jane.smith@example.com', '987-654-3210', '456 Elm St, Townsville', '2023-02-15');

-- Insert Sample Loans
INSERT INTO Loan (BookID, MemberID, LoanDate, DueDate, ReturnDate)
VALUES 
(1, 1, '2023-10-01', '2023-10-15', NULL),
(2, 2, '2023-10-05', '2023-10-20', NULL);

-- Insert Sample Fines
INSERT INTO Fine (LoanID, Amount, PaidStatus)
VALUES 
(1, 5.00, 'Unpaid');
