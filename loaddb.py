from dotenv import load_dotenv
from app import db

load_dotenv()
db.create_all()
