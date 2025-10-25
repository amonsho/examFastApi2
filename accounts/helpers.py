from passlib.hash import pbkdf2_sha256
from db_config import SessionLocal
from .models import UserModel

def hash_password(password:str):
    password_hash = pbkdf2_sha256.hash(password)
    return password_hash


def verify_password(password:str, password_hash:str):
    return pbkdf2_sha256.verify(password, password_hash)

def authenticate(username:str, password:str):
    db = SessionLocal()
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user:
        is_correct_password = verify_password(password, user.password)
        if is_correct_password:
            db.close()
            return user
    db.close()
    return None

