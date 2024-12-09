import sqlite3
from flask import Flask, jsonify, request, g
from datetime import datetime, timedelta

app = Flask(__name__)

# Database setup
DATABASE = 'library_system.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(error):
    if 'db' in g:
        g.db.close()

# Helper function to query the database
def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Create the database and tables (this can be done once during setup)
@app.before_first_request
def setup():
    db = get_db()
    with open('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()

# 1. Register a user
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    
    db = get_db()
    db.execute('INSERT INTO Users (name, email, password, role) VALUES (?, ?, ?, ?)', 
               (name, email, password, role))
    db.commit()
    
    return jsonify({'message': 'User created successfully'}), 201

# 2. Login User (basic auth)
@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = query_db('SELECT * FROM Users WHERE email = ? AND password = ?', [email, password], one=True)
    
    if user:
        return jsonify({'message': 'Login successful', 'user': {'id': user[0], 'name': user[1], 'role': user[4]}})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# 3. View all books
@app.route('/books', methods=['GET'])
def get_books():
    books = query_db('SELECT * FROM Books')
    return jsonify({'books': books})

# 4. User request a book
@app.route('/requests', methods=['POST'])
def request_book():
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    
    # Check if the book is available
    book = query_db('SELECT * FROM Books WHERE id = ?', [book_id], one=True)
    
    if book and book[4] > 0:  # Check if stock is available
        due_date = datetime.now() + timedelta(days=14)  # 2 weeks from now
        db = get_db()
        db.execute('INSERT INTO Requests (user_id, book_id, due_date) VALUES (?, ?, ?)', 
                   (user_id, book_id, due_date))
        db.execute('UPDATE Books SET stock = stock - 1 WHERE id = ?', [book_id])
        db.commit()
        return jsonify({'message': 'Book requested successfully'}), 201
    else:
        return jsonify({'message': 'Book is out of stock'}), 400

# 5. View user borrowing details
@app.route('/users/<int:user_id>/requests', methods=['GET'])
def get_user_requests(user_id):
    requests = query_db('SELECT * FROM Requests WHERE user_id = ?', [user_id])
    return jsonify({'requests': requests})

# 6. Admin manage book (add/update/delete)
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    published_year = data.get('published_year')
    stock = data.get('stock')
    
    db = get_db()
    db.execute('INSERT INTO Books (title, author, published_year, stock) VALUES (?, ?, ?, ?)', 
               (title, author, published_year, stock))
    db.commit()
    
    return jsonify({'message': 'Book added successfully'}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    published_year = data.get('published_year')
    stock = data.get('stock')
    
    db = get_db()
    db.execute('UPDATE Books SET title = ?, author = ?, published_year = ?, stock = ? WHERE id = ?',
               (title, author, published_year, stock, book_id))
    db.commit()
    
    return jsonify({'message': 'Book updated successfully'})

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    db = get_db()
    db.execute('DELETE FROM Books WHERE id = ?', [book_id])
    db.commit()
    
    return jsonify({'message': 'Book deleted successfully'})

# 7. Admin manage user requests (approve/reject)
@app.route('/requests/<int:request_id>', methods=['PUT'])
def manage_request(request_id):
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['approved', 'rejected']:
        return jsonify({'message': 'Invalid status'}), 400
    
    db = get_db()
    db.execute('UPDATE Requests SET status = ? WHERE id = ?', [status, request_id])
    db.commit()
    
    return jsonify({'message': 'Request status updated successfully'})

if __name__ == '__main__':
    app.run(debug=True)
