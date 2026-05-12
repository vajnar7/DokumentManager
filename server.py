from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Enum, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
import enum

Base = declarative_base()

class SectorEnum(enum.Enum):
    IT = 'IT'
    Kotlovnica = 'Kotlovnica'
    Elektricarji = 'Elektricarji'

# Define the User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

# Define the Documentation model
class Documentation(Base):
    __tablename__ = 'documentation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sector = Column(Enum(SectorEnum), nullable=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


def create_documentation_table(host, user, password, database, table_name='documentation'):
    """Create a MySQL table for storing documentation entries."""
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')
    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error creating table: {e}") from e


def insert_documentation_record(host, user, password, database, title, sector, content, author=None, table_name='documentation'):
    """Insert a new documentation entry into the documentation table."""
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        record = Documentation(title=title, sector=SectorEnum(sector), content=content, author=author)
        session.add(record)
        session.commit()
        return record.id
    except SQLAlchemyError as e:
        session.rollback()
        raise RuntimeError(f"Error inserting record: {e}") from e
    finally:
        session.close()


def search_documentation_records(host, user, password, database, search_string, table_name='documentation'):
    """Search the documentation table for records matching a string in title or content."""
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        results = session.query(Documentation).filter(
            (Documentation.title.like(f'%{search_string}%')) |
            (Documentation.content.like(f'%{search_string}%'))
        ).all()
        return [
            {
                'id': r.id,
                'title': r.title,
                'content': r.content,
                'author': r.author,
                'created_at': r.created_at,
                'updated_at': r.updated_at
            }
            for r in results
        ]
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error searching records: {e}") from e
    finally:
        session.close()


def register_user(host, user, password, database, username, user_password):
    """Register a new user."""
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            raise RuntimeError(f"User '{username}' already exists")
        
        # Hash the password
        hashed_password = generate_password_hash(user_password)
        
        # Create new user
        new_user = User(username=username, password=hashed_password)
        session.add(new_user)
        session.commit()
        return {'id': new_user.id, 'username': new_user.username}
    except SQLAlchemyError as e:
        session.rollback()
        raise RuntimeError(f"Error registering user: {e}") from e
    finally:
        session.close()


def authenticate_user(host, user, password, database, username, user_password):
    """Authenticate a user and return user data if successful."""
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        db_user = session.query(User).filter(User.username == username).first()
        if not db_user:
            raise RuntimeError(f"User '{username}' not found")
        
        if not check_password_hash(db_user.password, user_password):
            raise RuntimeError("Invalid password")
        
        return {'id': db_user.id, 'username': db_user.username}
    except SQLAlchemyError as e:
        raise RuntimeError(f"Error authenticating user: {e}") from e
    finally:
        session.close()


if __name__ == '__main__':
    # Example usage:
    # create_documentation_table('localhost', 'root', 'AldebaraN7#', 'docs_db')
    # insert_documentation_record('localhost', 'root', 'AldebaraN7#', 'docs_db', 'IP Address', 'IT', 'Moonstalker: 192.168.7.230, Zoran Robic: 192.168.7.75', 'Zoran Robic')
    records = search_documentation_records('localhost', 'root', 'AldebaraN7#', 'docs_db', 'IP')
    print(f"Najdeni zapisi:{records}")
    pass
