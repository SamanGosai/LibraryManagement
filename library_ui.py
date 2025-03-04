import streamlit as st
import pyodbc

# Database Connection
def connect_to_db():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=(localdb)\\localdb1;"
        "DATABASE=LibraryDB;"
        "UID=saman;"
        "PWD=12345678;"
    )
    return conn

st.title("📚 Library Management System")

# Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["Add Book", "View Books", "Add Member", "View Members", "Checkout Book", "Return Book", "Loan History", "Manage Fines"])

# Add a New Book
if menu == "Add Book":
    st.header("📖 Add a New Book")
    title = st.text_input("Title")
    author = st.text_input("Author")
    isbn = st.text_input("ISBN")
    genre = st.text_input("Genre")
    published_year = st.number_input("Published Year", min_value=1800, max_value=2025)
    if st.button("Add Book"):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Book (Title, Author, ISBN, Genre, PublishedYear, Status) VALUES (?, ?, ?, ?, ?, 'Available')",
            (title, author, isbn, genre, published_year)
        )
        conn.commit()
        st.success("✅ Book added successfully!")

# View All Books
if menu == "View Books":
    st.header("📚 All Books")
    search = st.text_input("Search by Title, Author, or ISBN")
    query = "SELECT * FROM Book WHERE Title LIKE ? OR Author LIKE ? OR ISBN LIKE ?"
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query, ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    books = cursor.fetchall()
    for book in books:
        st.write(f"📖 **{book.Title}** by {book.Author} | ISBN: {book.ISBN} | Status: {book.Status}")

# Add a New Member
if menu == "Add Member":
    st.header("👤 Add a New Member")
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    address = st.text_area("Address")
    if st.button("Register Member"):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Member (Name, Email, Phone, Address, MembershipStartDate) VALUES (?, ?, ?, ?, GETDATE())",
            (name, email, phone, address)
        )
        conn.commit()
        st.success("✅ Member registered successfully!")

# View All Members
if menu == "View Members":
    st.header("👥 All Members")
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Member")
    members = cursor.fetchall()
    for member in members:
        st.write(f"👤 **{member.Name}** | Email: {member.Email} | Phone: {member.Phone}")

# Checkout a Book
if menu == "Checkout Book":
    st.header("📖 Checkout a Book")
    book_id = st.number_input("Book ID", min_value=1)
    member_id = st.number_input("Member ID", min_value=1)
    if st.button("Checkout"):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Loan (BookID, MemberID, LoanDate, DueDate) VALUES (?, ?, GETDATE(), DATEADD(day, 14, GETDATE()))",
            (book_id, member_id)
        )
        cursor.execute("UPDATE Book SET Status = 'Checked Out' WHERE BookID = ?", (book_id,))
        conn.commit()
        st.success("✅ Book checked out successfully!")

# Return a Book
if menu == "Return Book":
    st.header("📖 Return a Book")
    book_id = st.number_input("Book ID", min_value=1)
    if st.button("Return"):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Loan SET ReturnDate = GETDATE() WHERE BookID = ? AND ReturnDate IS NULL", (book_id,))
        cursor.execute("UPDATE Book SET Status = 'Available' WHERE BookID = ?", (book_id,))
        conn.commit()
        st.success("✅ Book returned successfully!")

# View Loan History
if menu == "Loan History":
    st.header("📜 Loan History")
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Loan.LoanID, Book.Title, Member.Name, Loan.LoanDate, Loan.DueDate, Loan.ReturnDate FROM Loan JOIN Book ON Loan.BookID = Book.BookID JOIN Member ON Loan.MemberID = Member.MemberID")
    loans = cursor.fetchall()
    for loan in loans:
        return_status = "✅ Returned" if loan.ReturnDate else "❌ Not Returned"
        st.write(f"📖 **{loan.Title}** | Loaned to: {loan.Name} | Due Date: {loan.DueDate} | {return_status}")

# Manage Fines
if menu == "Manage Fines":
    st.header("💰 Manage Fines")
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Fine.FineID, Member.Name, Book.Title, Fine.Amount, Fine.PaidStatus FROM Fine JOIN Loan ON Fine.LoanID = Loan.LoanID JOIN Member ON Loan.MemberID = Member.MemberID JOIN Book ON Loan.BookID = Book.BookID WHERE Fine.PaidStatus = 'Unpaid'")
    fines = cursor.fetchall()
    for fine in fines:
        st.write(f"💸 Fine ID: {fine.FineID} | Member: {fine.Name} | Book: {fine.Title} | Amount: ${fine.Amount} | Status: {fine.PaidStatus}")
        if st.button(f"Mark Paid - Fine ID {fine.FineID}"):
            cursor.execute("UPDATE Fine SET PaidStatus = 'Paid' WHERE FineID = ?", (fine.FineID,))
            conn.commit()
            st.success(f"✅ Fine ID {fine.FineID} marked as paid!")

