from .models import UserModel, SessionModel,UserType
from .helpers import hash_password, verify_password, authenticate
from .schemas import CreateUserModelSchema, UserModelResponse, LoginUserModel
from db_config import get_db
from fastapi import Depends, HTTPException, Cookie, Response
from sqlalchemy.orm import Session
from fastapi import APIRouter
from .permissions import is_authenticated, is_admin, is_owner

user_admin = APIRouter()

@user_admin.post('/register')
async def register_endpoint(user:CreateUserModelSchema, db: Session = Depends(get_db)):
    role_value = user.role.lower()
    if role_value not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="invalid role")
    new_user = UserModel(username=user.username, email=user.email, password=hash_password(user.password), role = UserType(role_value))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Uzer registred successfully"}

@user_admin.post('/login')
async def login_endpoint(response:Response, user:LoginUserModel, db: Session = Depends(get_db)):
    login_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if not login_user or not verify_password(user.password, login_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = authenticate(user.username, user.password)
    new_session = SessionModel(user_id = login_user.id, token=token.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    response.set_cookie(key="session_token", value=token.id, httponly=True)
    return {"message": "login successfully"}

@user_admin.get('/me', dependencies=[Depends(is_authenticated)])
async def me_endpoint(current_user: UserModel = Depends(is_authenticated)):
    return UserModelResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )
    
@user_admin.post('/logout', dependencies=[Depends(is_authenticated)])
async def logout_endpoint(response:Response, session_token: str = Cookie(None), db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.token == session_token).first()
    if session:
        db.delete(session)
        db.commit()
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}

@user_admin.get('/admin/users', dependencies=[Depends(is_admin)])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return [UserModelResponse(id=user.id, username=user.username, email=user.email) for user in users]

@user_admin.delete('/admin/users/{user_id}', dependencies=[Depends(is_admin)])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


#-----------------------------------------------------------------------------
from .models import NotesModel
from .schemas import CreateNotesModelSchema, NotesModelResponse


@user_admin.post("/notes/create")
async def create_note(note:CreateNotesModelSchema, user=Depends(is_authenticated), db:Session = Depends(get_db)):
    new_note = NotesModel(title=note.title, content=note.content, user_id=user.id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {"message": "Note created successfully"}

@user_admin.get("/notes", response_model=list[NotesModelResponse])
async def get_notes(user=Depends(is_authenticated), db:Session = Depends(get_db)):
    notes = db.query(NotesModel).filter(NotesModel.user_id == user.id).all()
    return notes

@user_admin.put("/notes/{note_id}")
async def update_note(note_id:int, updated_note:CreateNotesModelSchema, user=Depends(is_authenticated), db:Session=Depends(get_db)):
    note = db.query(NotesModel).filter(NotesModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail='Note not found')
    if note.user_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot edit this note ")
    
    note.title = updated_note.title
    note.content = updated_note.content
    db.commit()
    return {"message": "Note updated succesfully"}

@user_admin.delete("notes/{note_id}")
async def delete_note(note_id:int, user=Depends(is_authenticated), db:Session=Depends(get_db)):
    note = db.query(NotesModel).filter(NotesModel.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note.user_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot delete this note")

    db.delete(note)
    db.commit()
    return {"message": "Note delete successfully"}
