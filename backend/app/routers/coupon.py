from fastapi import APIRouter, Depends, HTTPException
from .models import CouponGrab
from .routers.auth import get_current_user
import aiosqlite

router = APIRouter(prefix="/coupons", tags=["coupons"])

@router.get("/list")
async def list_coupons():
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM coupons")
        rows = await cursor.fetchall()
        return {"coupons": [dict(row) for row in rows]}

@router.post("/grab")
async def grab_coupon(coupon: CouponGrab, current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT id FROM users WHERE username = ?", (current_user,)
        )
        user_row = await cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")

        cursor = await db.execute(
            "SELECT * FROM coupons WHERE id = ?", (coupon.coupon_id,)
        )
        coupon_row = await cursor.fetchone()
        if not coupon_row:
            raise HTTPException(status_code=404, detail="Coupon not found")

        if coupon_row["remaining"] <= 0:
            raise HTTPException(status_code=400, detail="Coupon exhausted")

        cursor = await db.execute(
            "SELECT id FROM coupon_logs WHERE user_id = ? AND coupon_id = ?",
            (user_row["id"], coupon.coupon_id)
        )
        existing = await cursor.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Already grabbed this coupon")

        await db.execute(
            "UPDATE coupons SET remaining = remaining - 1 WHERE id = ? AND remaining > 0",
            (coupon.coupon_id,)
        )
        await db.execute(
            "INSERT INTO coupon_logs (user_id, coupon_id) VALUES (?, ?)",
            (user_row["id"], coupon.coupon_id)
        )
        await db.commit()

    return {"message": "Coupon grabbed successfully"}

@router.get("/my")
async def my_coupons(current_user: str = Depends(get_current_user)):
    async with aiosqlite.connect("db.sqlite3") as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT c.*, cl.grabbed_at FROM coupon_logs cl
            JOIN coupons c ON cl.coupon_id = c.id
            JOIN users u ON cl.user_id = u.id
            WHERE u.username = ?
            ORDER BY cl.grabbed_at DESC
        """, (current_user,))
        rows = await cursor.fetchall()
        return {"coupons": [dict(row) for row in rows]}