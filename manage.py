from db_config import engine
from fastapi import FastAPI
from accounts.models import BaseModel
import uvicorn
from accounts.views import user_admin

app = FastAPI()
app.include_router(prefix='/users', router=user_admin)

if __name__ == '__main__':
    BaseModel.metadata.create_all(bind=engine)
    uvicorn.run('manage:app', host='127.0.0.1', port=8000, reload=True)