from flask import Flask, request, jsonify, session, send_from_directory
from server import (
    create_documentation_table,
    insert_documentation_record,
    search_documentation_records,
    Documentation,
    User,
    SectorEnum,
    SQLAlchemyError,
    register_user,
    authenticate_user
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'AldebaraN7#')
DB_NAME = os.getenv('DB_NAME', 'docs_db')

# Set secret key for session management
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')


def get_session():
    """Create and return a database session."""
    engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
    Session = sessionmaker(bind=engine)
    return Session()


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('static', 'index.html')


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields: username, password'}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password cannot be empty'}), 400
        
        if len(password) < 4:
            return jsonify({'error': 'Password must be at least 4 characters long'}), 400
        
        user = register_user(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            username=username,
            user_password=password
        )
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user
        }), 201
    
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Login a user."""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields: username, password'}), 400
        
        username = data.get('username').strip()
        password = data.get('password')
        
        user = authenticate_user(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            username=username,
            user_password=password
        )
        
        # Store user in session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user
        }), 200
    
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout the current user."""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    """Get current logged-in user."""
    if 'username' in session:
        return jsonify({
            'success': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username')
            }
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Not logged in'
        }), 401


@app.route('/api/documents', methods=['POST'])
def create_document():
    """Insert a new documentation record."""
    try:
        # Check if user is logged in
        if 'username' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Missing required fields: title, content'}), 400
        
        title = data.get('title')
        content = data.get('content')
        sector = data.get('sector')
        author = session.get('username')  # Use logged-in user as author
        
        # Insert the record
        doc_id = insert_documentation_record(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            title=title,
            sector=sector,
            content=content,
            author=author
        )
        
        return jsonify({
            'success': True,
            'message': 'Document created successfully',
            'id': doc_id
        }), 201
    
    except ValueError as e:
        return jsonify({'error': f'Invalid sector value: {str(e)}'}), 400
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/documents/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    """Update an existing documentation record."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        session = get_session()
        
        try:
            # Find the document
            document = session.query(Documentation).filter(Documentation.id == doc_id).first()
            
            if not document:
                return jsonify({'error': f'Document with id {doc_id} not found'}), 404
            
            # Update fields if provided
            if 'title' in data:
                document.title = data['title']
            if 'content' in data:
                document.content = data['content']
            if 'sector' in data and data['sector']:
                document.sector = SectorEnum(data['sector'])
            if 'author' in data:
                document.author = data['author']
            
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Document updated successfully',
                'id': doc_id
            }), 200
        
        except ValueError as e:
            session.rollback()
            return jsonify({'error': f'Invalid sector value: {str(e)}'}), 400
        except SQLAlchemyError as e:
            session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a documentation record."""
    try:
        session = get_session()
        
        try:
            # Find the document
            document = session.query(Documentation).filter(Documentation.id == doc_id).first()
            
            if not document:
                return jsonify({'error': f'Document with id {doc_id} not found'}), 404
            
            # Delete the document
            session.delete(document)
            session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully',
                'id': doc_id
            }), 200
        
        except SQLAlchemyError as e:
            session.rollback()
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/documents/search', methods=['GET'])
def search_documents():
    """Search documentation records."""
    try:
        search_string = request.args.get('q', '')
        
        if not search_string:
            return jsonify({'error': 'Missing search query parameter: q'}), 400
        
        results = search_documentation_records(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            search_string=search_string
        )
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        }), 200
    
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Retrieve a specific documentation record."""
    try:
        session = get_session()
        
        try:
            document = session.query(Documentation).filter(Documentation.id == doc_id).first()
            
            if not document:
                return jsonify({'error': f'Document with id {doc_id} not found'}), 404
            
            return jsonify({
                'success': True,
                'document': {
                    'id': document.id,
                    'title': document.title,
                    'content': document.content,
                    'sector': document.sector.value if document.sector else None,
                    'author': document.author,
                    'created_at': document.created_at.isoformat() if document.created_at else None,
                    'updated_at': document.updated_at.isoformat() if document.updated_at else None
                }
            }), 200
        
        except SQLAlchemyError as e:
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all documentation records."""
    try:
        session = get_session()
        
        try:
            documents = session.query(Documentation).all()
            
            return jsonify({
                'success': True,
                'count': len(documents),
                'documents': [
                    {
                        'id': doc.id,
                        'title': doc.title,
                        'content': doc.content,
                        'sector': doc.sector.value if doc.sector else None,
                        'author': doc.author,
                        'created_at': doc.created_at.isoformat() if doc.created_at else None,
                        'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
                    }
                    for doc in documents
                ]
            }), 200
        
        except SQLAlchemyError as e:
            return jsonify({'error': f'Database error: {str(e)}'}), 500
        finally:
            session.close()
    
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({'error': 'Method not allowed'}), 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
