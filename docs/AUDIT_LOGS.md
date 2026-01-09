# Audit Log Reference

This document describes the structure and meaning of the JSON audit logs produced by the POC Web App backend.

## Overview

The backend uses **structured JSON logging** via `python-json-logger`. All logs are written to `stdout` and are automatically captured by Azure Container Apps Log Analytics when deployed.

---

## Log Structure

Every audit log entry is a JSON object with the following base fields:

| Key             | Type   | Description                                              | Example Values                                    |
| --------------- | ------ | -------------------------------------------------------- | ------------------------------------------------- |
| `asctime`       | string | Timestamp when the log was recorded (server time)        | `"2026-01-08T17:43:26"`                           |
| `levelname`     | string | Log level                                                | `"INFO"`, `"WARNING"`, `"ERROR"`                  |
| `message`       | string | Human-readable summary of the event                      | `"AUDIT: UPDATE_USER_ROLE"`, `"AUTH: USER_LOGIN"` |
| `Admin_User`    | string | Email of the user who performed the action               | `"admin@example.com"`                             |
| `Action`        | string | Type of action performed (see Action Types below)        | `"USER_LOGIN"`, `"CONFIG_CHANGE"`                 |
| `Target_Tenant` | string | Tenant/organization context (reserved for multi-tenancy) | `"default"`                                       |
| `Target_User`   | string | Email of the user affected by the action (if applicable) | `"user@example.com"` or `""`                      |
| `Timestamp`     | string | UTC timestamp in ISO 8601 format                         | `"2026-01-08T12:13:26.718333"`                    |

---

## Action Types

The `Action` field indicates what type of event occurred. Here are all possible values:

### Authentication Actions

| Action Value    | Description                 | Additional Fields       |
| --------------- | --------------------------- | ----------------------- |
| `USER_LOGIN`    | User successfully logged in | `Success`, `IP_Address` |
| `USER_REGISTER` | New user account created    | `Success`, `IP_Address` |
| `USER_LOGOUT`   | User logged out             | `Success`, `IP_Address` |

**Additional Fields for Auth Events:**

| Key          | Type    | Description                  | Example Values               |
| ------------ | ------- | ---------------------------- | ---------------------------- |
| `Success`    | boolean | Whether the action succeeded | `true`, `false`              |
| `IP_Address` | string  | Client IP address            | `"192.168.1.1"`, `"unknown"` |

---

### User Management Actions

| Action Value          | Description                 | Additional Fields |
| --------------------- | --------------------------- | ----------------- |
| `UPDATE_USER_ROLE`    | Admin changed a user's role | `Details`         |
| `UPDATE_USER_PROFILE` | User updated their profile  | `Details`         |

**Additional Fields for User Actions:**

| Key       | Type   | Description                   | Example Values                              |
| --------- | ------ | ----------------------------- | ------------------------------------------- |
| `Details` | object | Contains action-specific data | `{"old_role": "user", "new_role": "admin"}` |

---

### Configuration Actions

| Action Value    | Description                           | Additional Fields                      |
| --------------- | ------------------------------------- | -------------------------------------- |
| `CONFIG_CHANGE` | Admin modified a system configuration | `Config_Key`, `Old_Value`, `New_Value` |

**Additional Fields for Config Events:**

| Key          | Type   | Description                                | Example Values                                |
| ------------ | ------ | ------------------------------------------ | --------------------------------------------- |
| `Config_Key` | string | The configuration setting that was changed | `"theme"`, `"app_name"`, `"maintenance_mode"` |
| `Old_Value`  | string | Previous value before the change           | `"dark"`, `"false"`                           |
| `New_Value`  | string | New value after the change                 | `"light"`, `"true"`                           |

---

## Example Log Entries

### 1. User Login

```json
{
  "asctime": "2026-01-08T17:45:17",
  "levelname": "INFO",
  "message": "AUTH: USER_LOGIN",
  "Admin_User": "user@example.com",
  "Action": "USER_LOGIN",
  "Target_Tenant": "default",
  "Target_User": "user@example.com",
  "Success": true,
  "IP_Address": "unknown",
  "Timestamp": "2026-01-08T12:15:17.112038"
}
```

### 2. Role Change

```json
{
  "asctime": "2026-01-08T17:44:09",
  "levelname": "INFO",
  "message": "AUDIT: UPDATE_USER_ROLE",
  "Admin_User": "admin@example.com",
  "Action": "UPDATE_USER_ROLE",
  "Target_Tenant": "default",
  "Target_User": "user@example.com",
  "Timestamp": "2026-01-08T12:14:09.435125",
  "Details": {
    "old_role": "manager",
    "new_role": "editor"
  }
}
```

### 3. Configuration Change

```json
{
  "asctime": "2026-01-08T17:43:32",
  "levelname": "INFO",
  "message": "CONFIG: Changed theme",
  "Admin_User": "admin@example.com",
  "Action": "CONFIG_CHANGE",
  "Target_Tenant": "default",
  "Target_User": "",
  "Config_Key": "theme",
  "Old_Value": "dark",
  "New_Value": "light",
  "Timestamp": "2026-01-08T12:13:32.740851"
}
```

---

## Querying Logs in Azure Log Analytics

Once deployed to Azure Container Apps, use this KQL query to view audit logs:

```kql
ContainerAppConsoleLogs_CL
| extend d = parse_json(Log_s)
| project Time = TimeGenerated,
    Admin = tostring(d.Admin_User),
    Action = tostring(d.Action),
    Target = tostring(d.Target_User),
    Details = tostring(d.Details)
| where isnotempty(Admin)
| order by Time desc
```

---

## Security Notes

1. **Immutability**: Once logs are written to Azure Log Analytics, they cannot be modified or deleted by application users.
2. **Retention**: Configure your Log Analytics workspace retention policy according to your compliance requirements.
3. **Sensitive Data**: Passwords and tokens are never logged. Only metadata (email, action type, timestamps) is recorded.
