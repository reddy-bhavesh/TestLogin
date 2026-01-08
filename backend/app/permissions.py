"""
Role-Based Access Control (RBAC) Permissions
Defines what each role can and cannot do
"""
from enum import Enum
from typing import List

class Permission(str, Enum):
    # Config permissions
    VIEW_CONFIG = "view_config"
    EDIT_CONFIG = "edit_config"
    
    # User management permissions
    VIEW_USERS = "view_users"
    EDIT_USERS = "edit_users"
    CHANGE_ROLES = "change_roles"
    
    # Profile permissions
    VIEW_OWN_PROFILE = "view_own_profile"
    EDIT_OWN_PROFILE = "edit_own_profile"

# Role permission mapping
ROLE_PERMISSIONS = {
    "admin": [
        Permission.VIEW_CONFIG,
        Permission.EDIT_CONFIG,
        Permission.VIEW_USERS,
        Permission.EDIT_USERS,
        Permission.CHANGE_ROLES,
        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
    ],
    "manager": [
        Permission.VIEW_CONFIG,
        Permission.VIEW_USERS,
        Permission.EDIT_USERS,
        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
    ],
    "editor": [
        Permission.VIEW_USERS,
        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
    ],
    "user": [
        Permission.VIEW_OWN_PROFILE,
        Permission.EDIT_OWN_PROFILE,
    ],
    "viewer": [
        Permission.VIEW_OWN_PROFILE,
        # Cannot edit own profile - read only
    ],
}

def has_permission(role: str, permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    role_perms = ROLE_PERMISSIONS.get(role, [])
    return permission in role_perms

def get_permissions(role: str) -> List[Permission]:
    """Get all permissions for a role"""
    return ROLE_PERMISSIONS.get(role, [])

def can_access_config(role: str) -> bool:
    """Check if role can access config page"""
    return has_permission(role, Permission.VIEW_CONFIG)

def can_edit_config(role: str) -> bool:
    """Check if role can edit configurations"""
    return has_permission(role, Permission.EDIT_CONFIG)

def can_view_users(role: str) -> bool:
    """Check if role can view user list"""
    return has_permission(role, Permission.VIEW_USERS)

def can_edit_users(role: str) -> bool:
    """Check if role can edit other users"""
    return has_permission(role, Permission.EDIT_USERS)

def can_change_roles(role: str) -> bool:
    """Check if role can change user roles"""
    return has_permission(role, Permission.CHANGE_ROLES)

def can_edit_own_profile(role: str) -> bool:
    """Check if role can edit own profile"""
    return has_permission(role, Permission.EDIT_OWN_PROFILE)
