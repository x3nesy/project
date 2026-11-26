from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from passlib.context import CryptContext

app = FastAPI(title="Platform API")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

USERS_DB = {
    "student": {
        "id": 1, "name": "Иван Студент", "role": "student", 
        "hashed_password": get_password_hash("password123")
    },
    "teacher_do": {
        "id": 2, "name": "Мария ДО", "role": "teacher_do", 
        "hashed_password": get_password_hash("password123")
    },
    "teacher_subj": {
        "id": 3, "name": "Петр Предметник", "role": "teacher_subj", 
        "hashed_password": get_password_hash("password123")
    },
    "organizer": {
        "id": 4, "name": "Олег Организатор", "role": "organizer", 
        "hashed_password": get_password_hash("password123")
    },
    "admin": {
        "id": 5, "name": "Анна Админ", "role": "admin", 
        "hashed_password": get_password_hash("password123")
    }
}

EVENTS_DB = {}

class EventCreate(BaseModel):
    title: str
    description: str

class EventResponse(BaseModel):
    id: int
    title: str
    creator_id: int

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = USERS_DB.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный токен или пользователь не найден")
    return user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    return {"access_token": form_data.username, "token_type": "bearer"}

def require_staff(user: dict = Depends(get_current_user)):
    if user["role"] not in ["teacher_do", "teacher_subj", "organizer", "admin"]:
        raise HTTPException(status_code=403, detail="Студенты не могут выполнять это действие")
    return user

def check_event_owner(event_id: int, user: dict = Depends(get_current_user)):
    if event_id not in EVENTS_DB:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    event = EVENTS_DB[event_id]
    if user["role"] != "admin" and event["creator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Вы не можете управлять чужим событием")
    return event

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/events", response_model=List[EventResponse])
def list_events(user: dict = Depends(get_current_user)):
    return [{"id": k, **v} for k, v in EVENTS_DB.items()]

@app.post("/events")
def create_event(event: EventCreate, user: dict = Depends(require_staff)):
    event_id = len(EVENTS_DB) + 1
    EVENTS_DB[event_id] = {
        "title": event.title, "description": event.description, "creator_id": user["id"]
    }
    return {"message": "Событие создано", "id": event_id}

@app.put("/events/{event_id}")
def update_event(event_id: int, event_data: EventCreate, event: dict = Depends(check_event_owner)):
    EVENTS_DB[event_id]["title"] = event_data.title
    return {"message": "Событие обновлено"}

@app.post("/events/{event_id}/attendance")
def mark_attendance(event_id: int, event: dict = Depends(check_event_owner)):
    return {"message": "Посещение отмечено"}

@app.get("/grades")
def get_grades(user: dict = Depends(get_current_user)):
    if user["role"] not in ["admin", "teacher_do"]:
        raise HTTPException(status_code=403, detail="Доступ к журналу оценок запрещен")
    return {"grades": [5, 4, 3, 5]}