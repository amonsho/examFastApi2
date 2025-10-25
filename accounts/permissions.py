from fastapi import Depends, Request, Response, HTTPException, status
from db_config import get_db
from .models import SessionModel, UserType

def is_authenticated(request:Request):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Not Authorized'
    )
    session_id = request.cookies.get('session_token')
    if not session_id:
        raise credentials_error
    db = next(get_db())
    session = db.query(SessionModel).filter(SessionModel.token == session_id).first()
    if not session:
        raise credentials_error
    return session.user 

def is_admin(user=Depends(is_authenticated)):
    if user.role != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin access required'
        )
    return True

def is_owner(user=Depends(is_authenticated)):
    if str(user.role).lower() != UserType.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to access this resource'
        )
    return True 


