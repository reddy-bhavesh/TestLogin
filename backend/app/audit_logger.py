"""
Audit Logger for Admin Actions
Outputs JSON-formatted logs to stdout for Azure Container Apps Log Analytics
"""
import logging
import sys
from pythonjsonlogger import jsonlogger

# Create audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Prevent duplicate handlers
if not audit_logger.handlers:
    # StreamHandler outputs to stdout (Azure Container Apps captures this)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    handler.setFormatter(formatter)
    audit_logger.addHandler(handler)

def log_admin_action(
    admin_user: str,
    action: str,
    target_tenant: str = None,
    target_user: str = None,
    details: dict = None
):
    """
    Log an admin action with structured audit fields.
    
    Args:
        admin_user: Email of the admin performing the action
        action: Description of the action (e.g., "UPDATE_USER_ROLE")
        target_tenant: Tenant/organization being affected (optional)
        target_user: User being affected (optional)
        details: Additional details (optional)
    """
    extra = {
        "Admin_User": admin_user,
        "Action": action,
        "Target_Tenant": target_tenant or "default",
        "Target_User": target_user or "",
    }
    
    if details:
        extra["Details"] = details
    
    audit_logger.info(f"AUDIT: {action}", extra=extra)

def log_auth_event(email: str, event_type: str, success: bool, ip_address: str = None):
    """Log authentication events (login, register, logout)"""
    extra = {
        "Admin_User": email,
        "Action": event_type,
        "Target_Tenant": "default",
        "Target_User": email,
        "Success": success,
        "IP_Address": ip_address or "unknown",
    }
    
    audit_logger.info(f"AUTH: {event_type}", extra=extra)

def log_config_change(admin_user: str, config_key: str, old_value: str, new_value: str):
    """Log configuration changes"""
    extra = {
        "Admin_User": admin_user,
        "Action": "CONFIG_CHANGE",
        "Target_Tenant": "default",
        "Target_User": "",
        "Config_Key": config_key,
        "Old_Value": old_value,
        "New_Value": new_value,
    }
    
    audit_logger.info(f"CONFIG: Changed {config_key}", extra=extra)
