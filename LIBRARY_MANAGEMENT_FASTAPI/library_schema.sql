CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(150) NOT NULL,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    total_copies INT NOT NULL,
    available_copies INT NOT NULL,
    published_year INT NOT NULL,
    CONSTRAINT fk_book_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id),
    CONSTRAINT chk_total_copies CHECK (total_copies >= 1),
    CONSTRAINT chk_available_copies CHECK (available_copies >= 0),
    CONSTRAINT chk_available_total CHECK (available_copies <= total_copies)
);

CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(15) NOT NULL,
    address VARCHAR(255) NOT NULL,
    membership_date DATE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE borrow_records (
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Borrowed',
    CONSTRAINT fk_borrow_book
        FOREIGN KEY (book_id) REFERENCES books(book_id),
    CONSTRAINT fk_borrow_member
        FOREIGN KEY (member_id) REFERENCES members(member_id)
);

INSERT INTO categories (category_name, description) VALUES
('Fiction', 'Fiction and novels'),
('Science', 'Science and technology books'),
('History', 'Historical books');

INSERT INTO books
(title, author, isbn, category_id, total_copies, available_copies, published_year)
VALUES
('Malgudi Days', 'R. K. Narayan', '9788185986170', 1, 5, 5, 1943),
('Wings of Fire', 'A. P. J. Abdul Kalam', '9788173711466', 2, 4, 4, 1999),
('India After Gandhi', 'Ramachandra Guha', '9780330500388', 3, 3, 3, 2007),
('The Guide', 'R. K. Narayan', '9788185986163', 1, 2, 2, 1958),
('A Brief History of Time', 'Stephen Hawking', '9780553380163', 2, 3, 3, 1988);

INSERT INTO members
(name, email, phone, address, membership_date, is_active)
VALUES
('Rahul Sharma', 'rahul@example.com', '9876543210', 'Hyderabad', '2026-09-01', TRUE),
('Priya Reddy', 'priya@example.com', '9876543211', 'Hyderabad', '2026-09-02', TRUE),
('Arjun Kumar', 'arjun@example.com', '9876543212', 'Secunderabad', '2026-09-03', TRUE);
