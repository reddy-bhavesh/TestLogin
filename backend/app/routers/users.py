from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os

from app.models.database import get_db
from app.models.user import User, UserRole
from app.schemas import UserResponse, UserUpdate, UserRoleUpdate
from app.routers.auth import get_current_user
from app.audit_logger import log_admin_action
from app.permissions import can_edit_own_profile, can_view_users, can_change_roles

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user can edit their own profile
    if not can_edit_own_profile(current_user.role):
        raise HTTPException(status_code=403, detail="Your role does not allow profile editing")
    
    # Update all profile fields
    fields_updated = []
    
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
        fields_updated.append("full_name")
    if user_data.phone is not None:
        current_user.phone = user_data.phone
        fields_updated.append("phone")
    if user_data.address is not None:
        current_user.address = user_data.address
        fields_updated.append("address")
    if user_data.city is not None:
        current_user.city = user_data.city
        fields_updated.append("city")
    if user_data.country is not None:
        current_user.country = user_data.country
        fields_updated.append("country")
    if user_data.department is not None:
        current_user.department = user_data.department
        fields_updated.append("department")
    if user_data.job_title is not None:
        current_user.job_title = user_data.job_title
        fields_updated.append("job_title")
    if user_data.date_of_birth is not None:
        current_user.date_of_birth = user_data.date_of_birth
        fields_updated.append("date_of_birth")
    
    db.commit()
    db.refresh(current_user)
    
    # Audit log for profile update
    if fields_updated:
        log_admin_action(
            admin_user=current_user.email,
            action="UPDATE_PROFILE",
            target_user=current_user.email,
            details={"fields_updated": fields_updated}
        )
    
    return current_user

@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # For POC: save locally. In production: Azure Blob Storage
    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"{current_user.id}_{file.filename}"
    filepath = os.path.join(upload_dir, filename)
    
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)
    
    current_user.avatar_url = f"/uploads/avatars/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not can_view_users(current_user.role):
        raise HTTPException(status_code=403, detail="You don't have permission to view users")
    
    users = db.query(User).all()
    return users

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not can_change_roles(current_user.role):
        raise HTTPException(status_code=403, detail="You don't have permission to change roles")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role_data.role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    old_role = user.role
    user.role = role_data.role
    db.commit()
    db.refresh(user)
    
    # Audit log
    log_admin_action(
        admin_user=current_user.email,
        action="UPDATE_USER_ROLE",
        target_user=user.email,
        details={"old_role": old_role, "new_role": role_data.role}
    )
    
    return user
