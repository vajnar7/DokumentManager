# User Authentication Setup Guide

## Overview
The application now includes user authentication and document authorship tracking. Users must log in before accessing the document management system.

## New Features

### 1. User Registration & Login
- New users can register with a username and password
- Passwords are securely hashed using Werkzeug
- Users must log in to access the document manager

### 2. Automatic Document Authorship
- When creating a new document, the currently logged-in user is automatically set as the author
- No need to manually enter the author name
- Author field is removed from the UI form

### 3. Document Authorization
- Only the document author (the user who created it) can edit or delete their documents
- Other users can view documents but cannot modify them
- Attempting to edit/delete someone else's document returns a 403 Forbidden error
- The UI only shows edit/delete buttons for documents you created

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Make sure `Werkzeug==2.3.7` is installed (for password hashing).

### 2. Database Setup
Before running the application for the first time, create the database tables:

```bash
python -c "from server import create_documentation_table; create_documentation_table('localhost', 'root', 'AldebaraN7#', 'docs_db')"
```

This will create:
- `users` table with: id, username, password, created_at
- `documentation` table with: id, sector, title, content, author, created_at, updated_at

### 3. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### First Time User
1. Go to `http://localhost:5000`
2. Click "Register here" link
3. Enter a username and password (minimum 4 characters)
4. Click "Register"
5. Log in with your new credentials

### Returning User
1. Go to `http://localhost:5000`
2. Enter username and password
3. Click "Login"
4. You'll be taken to the document manager

### Managing Documents
1. Once logged in, you can:
   - Add new documents (author is auto-filled with your username)
   - Edit your own documents
   - Delete your own documents
   - Search documents (view all documents)

2. All documents show:
   - Title
   - Sector (IT, Kotlovnica, Elektricarji)
   - Author (logged-in user who created it)
   - Creation and update timestamps
   - Edit and Delete buttons (only visible if you are the author)
   - "Not your document" indicator (if you are not the author)

### Logout
Click the "Logout" button in the top-right corner to log out and return to the login page.

## API Endpoints

### Authentication Endpoints
- `POST /api/register` - Register new user
- `POST /api/login` - Log in user
- `POST /api/logout` - Log out user
- `GET /api/current-user` - Get current logged-in user

### Document Endpoints
- `GET /api/documents` - List all documents
- `POST /api/documents` - Create new document (requires login)
- `GET /api/documents/<id>` - Get specific document
- `PUT /api/documents/<id>` - Update document (requires login, author only)
- `DELETE /api/documents/<id>` - Delete document (requires login, author only)
- `GET /api/documents/search?q=query` - Search documents

## Security Considerations

### Current Implementation
- Passwords are hashed using werkzeug.security
- User sessions are stored server-side
- Session data is encrypted

### For Production Use
1. Change the `SECRET_KEY` in app.py (currently set to default):
   ```python
   app.secret_key = os.getenv('SECRET_KEY', 'your-unique-secret-key')
   ```

2. Set environment variables:
   ```bash
   export SECRET_KEY='your-long-random-secret-key'
   export DB_HOST='production-db-host'
   export DB_USER='production-user'
   export DB_PASSWORD='secure-password'
   export DB_NAME='production-db'
   ```

3. Use HTTPS for all connections
4. Implement password strength requirements
5. Add rate limiting for login attempts
6. Consider implementing user roles and permissions

## Troubleshooting

### "You can only edit documents you created"
- You attempted to edit a document that you did not create
- Only the author of a document can edit it

### "You can only delete documents you created"
- You attempted to delete a document that you did not create
- Only the author of a document can delete it

### "User 'username' already exists"
- The username is taken. Try a different username.

### "Invalid password"
- The password is incorrect. Try again or reset your password.

### "User not logged in"
- Your session has expired. Log in again.

### Database connection errors
- Verify MySQL is running
- Check database credentials in app.py or environment variables
- Ensure the database exists

### Tables not created
- Run the setup command mentioned in step 2 of Installation
- Check database permissions

## Files Modified

- `server.py` - Added User model and authentication functions
- `app.py` - Added authentication endpoints and session management; updated PUT and DELETE endpoints to require user to be logged in and be the document author
- `static/index.html` - Added login/register UI
- `static/js/app.js` - Added authentication JavaScript logic; updated document display to conditionally show edit/delete buttons based on document authorship
- `static/css/style.css` - Added login page styling and "not author" indicator styling
- `requirements.txt` - Added Werkzeug dependency
