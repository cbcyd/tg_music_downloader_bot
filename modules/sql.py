# Required imports from sqlalchemy for database interactions
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String

# Define the database connection string
sqlite_database = "sqlite:///users.db"
# Create an engine instance
engine = create_engine(sqlite_database)

# Base class for our ORM models
class Base(DeclarativeBase): pass

# Messages ORM model
class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)  # ID of the message
    client = Column(Integer)

# Create all tables in the database which are defined as DeclarativeBase
Base.metadata.create_all(bind=engine)

# Function to read a client by user_id
def read_client(user_id):
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if user:
            return user.client
        else:
            return None

# Function to update a client by user_id, or create a new record if user_id does not exist
def update_or_create_client(user_id, new_client):
    with Session(autoflush=False, bind=engine) as db:
        user = db.query(Users).filter(Users.user_id == user_id).first()
        if user:
            user.client = new_client
        else:
            user = Users(user_id=user_id, client=new_client)
            db.add(user)
        db.commit()
        return True