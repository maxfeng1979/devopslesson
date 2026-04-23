from fastapi import APIRouter, Depends, Query
from .routers.auth import get_current_user
import aiosqlite

router = APIRouter(prefix="/query", tags=["query"])

@router.get("/forms")
async def query_forms(keyword: str = Query(None), current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        if keyword:
            cursor = await db.execute("""
                SELECT f.*, u.username FROM forms f
                JOIN users u ON f.user_id = u.id
                WHERE f.name LIKE ? OR f.contact LIKE ? OR f.note LIKE ?
                ORDER BY f.created_at DESC
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        else:
            cursor = await db.execute("""
                SELECT f.*, u.username FROM forms f
                JOIN users u ON f.user_id = u.id
                ORDER BY f.created_at DESC
            """)
        rows = await cursor.fetchall()
        return {"forms": [dict(row) for row in rows]}

@router.get("/coupons")
async def query_coupons(keyword: str = Query(None), current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        if keyword:
            cursor = await db.execute("""
                SELECT c.*, cl.grabbed_at, u.username FROM coupon_logs cl
                JOIN coupons c ON cl.coupon_id = c.id
                JOIN users u ON cl.user_id = u.id
                WHERE c.name LIKE ?
                ORDER BY cl.grabbed_at DESC
            """, (f"%{keyword}%",))
        else:
            cursor = await db.execute("""
                SELECT c.*, cl.grabbed_at, u.username FROM coupon_logs cl
                JOIN coupons c ON cl.coupon_id = c.id
                JOIN users u ON cl.user_id = u.id
                ORDER BY cl.grabbed_at DESC
            """)
        rows = await cursor.fetchall()
        return {"coupons": [dict(row) for row in rows]}