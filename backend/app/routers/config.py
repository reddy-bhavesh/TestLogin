from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.user import User, UserRole, SystemConfig
from app.schemas import ConfigItem, ConfigResponse
from app.routers.auth import get_current_user
from app.audit_logger import log_config_change
from app.permissions import can_access_config, can_edit_config

router = APIRouter()

# Default system configurations
DEFAULT_CONFIGS = [
    {"key": "app_name", "value": "POC Web App", "description": "Application name"},
    {"key": "theme", "value": "dark", "description": "UI theme (light/dark)"},
    {"key": "maintenance_mode", "value": "false", "description": "Enable maintenance mode"},
    {"key": "max_upload_size", "value": "5242880", "description": "Max file upload size in bytes"},
]

def init_default_configs(db: Session):
    """Initialize default configurations if not exist"""
    for config in DEFAULT_CONFIGS:
        existing = db.query(SystemConfig).filter(SystemConfig.key == config["key"]).first()
        if not existing:
            db_config = SystemConfig(**config)
            db.add(db_config)
    db.commit()

@router.get("/", response_model=List[ConfigResponse])
def get_all_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not can_access_config(current_user.role):
        raise HTTPException(status_code=403, detail="You don't have permission to view configuration")
    
    init_default_configs(db)
    configs = db.query(SystemConfig).all()
    return configs

@router.get("/{key}", response_model=ConfigResponse)
def get_config(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config

@router.put("/{key}", response_model=ConfigResponse)
def update_config(
    key: str,
    config_data: ConfigItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not can_edit_config(current_user.role):
        raise HTTPException(status_code=403, detail="You don't have permission to edit configuration")
    
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    old_value = config.value if config else None
    
    if not config:
        # Create new config
        config = SystemConfig(key=key, value=config_data.value, description=config_data.description)
        db.add(config)
    else:
        config.value = config_data.value
        if config_data.description:
            config.description = config_data.description
    
    db.commit()
    db.refresh(config)
    
    # Audit log
    log_config_change(current_user.email, key, old_value or "(new)", config_data.value)
    
    return config

@router.post("/", response_model=ConfigResponse)
def create_config(
    config_data: ConfigItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    existing = db.query(SystemConfig).filter(SystemConfig.key == config_data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Configuration key already exists")
    
    config = SystemConfig(**config_data.model_dump())
    db.add(config)
    db.commit()
    db.refresh(config)
    return config
