from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..auth import verify_password, get_password_hash, create_access_token, decode_token
from ..models import UserCreate, UserLogin, Token
from ..database import get_db
import aiosqlite

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = decode_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

@router.post("/register", status_code=201)
async def register(user: UserCreate):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id FROM users WHERE username = ?", (user.username,)
        )
        existing = await cursor.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        password_hash = get_password_hash(user.password)
        await db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (user.username, password_hash)
        )
        await db.commit()
    return {"message": "User created successfully"}

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?", (user.username,)
        )
        row = await cursor.fetchone()
        if not row or not verify_password(user.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}