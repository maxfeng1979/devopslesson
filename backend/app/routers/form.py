from fastapi import APIRouter, Depends, HTTPException
from ..models import FormSubmit
from ..routers.auth_routes import get_current_user
import aiosqlite

router = APIRouter(prefix="/form", tags=["form"])

@router.post("/submit")
async def submit_form(form: FormSubmit, current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id FROM users WHERE username = ?", (current_user,)
        )
        user_row = await cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")

        await db.execute(
            "INSERT INTO forms (user_id, name, contact, note) VALUES (?, ?, ?, ?)",
            (user_row["id"], form.name, form.contact, form.note)
        )
        await db.commit()
    return {"message": "Form submitted successfully"}

@router.get("/list")
async def list_forms(current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT f.*, u.username FROM forms f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
        """)
        rows = await cursor.fetchall()
        return {"forms": [dict(row) for row in rows]}