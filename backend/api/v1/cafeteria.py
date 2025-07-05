#
#
#
# @router.delete("/{user_id}", status_code=204)
# async def delete_user_view(
#     user_id: int,
#     db: AsyncSession = Depends(get_pg_db),
#     current_user: User = Depends(get_current_user),
# ):
#     if current_user.role != "admin":
#         raise HTTPException(status_code=403, detail="Not enough permissions")
#     await delete_user(db, user_id)
#     return None
#
# async def delete_user(db: AsyncSession, user_id: int):
#     user = await get_user(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     await db.delete(user)
#     await db.commit()
