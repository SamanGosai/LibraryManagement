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
menu = st.sidebar.radio("Navigation", [
    "Add Book", "View Books", 
    "Add Member", "View Members",
    "Checkout Book", "Return Book", "Loan History", "Manage Fines"
])

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

# View All Books with Delete Option
if menu == "View Books":
    st.header("📚 All Books")
    search = st.text_input("Search by Title, Author, or ISBN")

    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT BookID, Title, Author, ISBN, Genre, PublishedYear, Status FROM Book WHERE Title LIKE ? OR Author LIKE ? OR ISBN LIKE ?"
    cursor.execute(query, ('%' + search + '%', '%' + search + '%', '%' + search + '%'))
    books = cursor.fetchall()

    for book in books:
        col1, col2 = st.columns([4, 1])  # Create columns for layout
        with col1:
            st.write(f"📖 **{book.Title}** by {book.Author} | ISBN: {book.ISBN} | Status: {book.Status}")
        with col2:
            if st.button(f"🗑️ Delete", key=f"delete_{book.BookID}"):
                cursor.execute("DELETE FROM Book WHERE BookID = ?", (book.BookID,))
                conn.commit()
                st.success(f"✅ Book '{book.Title}' deleted successfully!")
                st.rerun()
  # Refresh the page

    conn.close()

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

    # Fetch available books
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT BookID, Title FROM Book WHERE Status = 'Available'")
    available_books = cursor.fetchall()

    # Fetch members
    cursor.execute("SELECT MemberID, Name FROM Member")
    members = cursor.fetchall()
    conn.close()

    # Dropdowns for book and member selection
    book_options = {str(book.BookID): book.Title for book in available_books}
    member_options = {str(member.MemberID): member.Name for member in members}

    book_id = st.selectbox("Select a Book", options=list(book_options.keys()), format_func=lambda x: book_options[x]) if book_options else None
    member_id = st.selectbox("Select a Member", options=list(member_options.keys()), format_func=lambda x: member_options[x]) if member_options else None

    if st.button("Checkout") and book_id and member_id:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Loan (BookID, MemberID, LoanDate, DueDate) VALUES (?, ?, GETDATE(), DATEADD(day, 14, GETDATE()))",
            (book_id, member_id)
        )
        cursor.execute("UPDATE Book SET Status = 'Checked Out' WHERE BookID = ?", (book_id,))
        conn.commit()
        conn.close()
        st.success("✅ Book checked out successfully!")
        st.rerun()  # Refresh page

# Return a Book
if menu == "Return Book":
    st.header("📖 Return a Book")

    # Fetch books that are currently checked out (based on Loan table, not Book status)
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Book.BookID, Book.Title
        FROM Loan
        JOIN Book ON Loan.BookID = Book.BookID
        WHERE Loan.ReturnDate IS NULL
    """)
    checked_out_books = cursor.fetchall()
    conn.close()

    # Dropdown for book selection
    book_options = {str(book.BookID): book.Title for book in checked_out_books}

    book_id = st.selectbox("Select a Book to Return", options=list(book_options.keys()), format_func=lambda x: book_options[x]) if book_options else None

    if st.button("Return") and book_id:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE Loan SET ReturnDate = GETDATE() WHERE BookID = ? AND ReturnDate IS NULL", (book_id,))
        cursor.execute("UPDATE Book SET Status = 'Available' WHERE BookID = ?", (book_id,))
        conn.commit()
        conn.close()
        st.success("✅ Book returned successfully!")
        st.rerun()  # Refresh page

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

