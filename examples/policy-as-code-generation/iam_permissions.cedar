// Cedar Policy Language - IAM Permissions for AI Development Platform
// Generated from compliance requirements using AI assistance

// User Authentication Policies
permit(
    principal == User::"authenticated",
    action in [Action::"read_profile", Action::"update_profile"],
    resource == User::"self"
);

forbid(
    principal == User::"authenticated", 
    action == Action::"delete_profile",
    resource == User::"self"
) when {
    principal.role != "admin"
};

// Admin User Management
permit(
    principal,
    action in [
        Action::"create_user",
        Action::"read_user", 
        Action::"update_user",
        Action::"delete_user",
        Action::"list_users"
    ],
    resource == User::"any"
) when {
    principal.role == "admin"
};

// API Access Controls
permit(
    principal == User::"authenticated",
    action in [
        Action::"read_api_docs",
        Action::"access_public_endpoints"
    ],
    resource == API::"public"
);

permit(
    principal == User::"authenticated",
    action in [
        Action::"call_protected_endpoints",
        Action::"access_user_data"
    ],
    resource == API::"protected"
) when {
    principal.token_valid == true &&
    principal.token_expired == false
};

// Data Access Policies  
permit(
    principal == User::"authenticated",
    action in [Action::"read", Action::"update"],
    resource
) when {
    resource.owner == principal.id ||
    resource.shared_with has principal.id
};

forbid(
    principal == User::"authenticated",
    action == Action::"delete", 
    resource
) when {
    resource.type == "critical_data" &&
    principal.role != "admin"
};

// Time-based Access Controls
forbid(
    principal,
    action,
    resource
) when {
    context.current_time < datetime("2024-01-01T00:00:00Z") ||
    context.current_time > datetime("2025-12-31T23:59:59Z")
};

// Rate Limiting Policy
forbid(
    principal == User::"authenticated",
    action == Action::"api_call",
    resource == API::"any"
) when {
    context.request_count > 1000 &&
    context.time_window == "1hour"
};

// Security Context Requirements
permit(
    principal == User::"authenticated",
    action,
    resource
) when {
    context.connection_secure == true &&
    context.user_agent != "" &&
    context.source_ip in ipaddr("10.0.0.0/8")
};

// Multi-factor Authentication Requirements
forbid(
    principal == User::"authenticated",
    action in [
        Action::"delete_user",
        Action::"change_password", 
        Action::"update_security_settings"
    ],
    resource
) when {
    principal.mfa_verified != true
};

// Audit Logging Requirements
permit(
    principal,
    action,
    resource
) when {
    action in [
        Action::"create",
        Action::"update", 
        Action::"delete",
        Action::"admin_action"
    ]
} unless {
    context.audit_disabled == true
};

// Emergency Access Override
permit(
    principal == User::"emergency_admin",
    action,
    resource  
) when {
    context.emergency_mode == true &&
    context.emergency_justification != ""
};

// Service Account Policies
permit(
    principal == ServiceAccount::"ci_cd",
    action in [
        Action::"deploy_application",
        Action::"run_tests",
        Action::"access_build_artifacts"
    ],
    resource == Infrastructure::"development"
);

forbid(
    principal == ServiceAccount::"ci_cd",
    action in [
        Action::"access_production_data",
        Action::"modify_user_accounts"
    ],
    resource
);

// Cross-Origin Request Policy
forbid(
    principal,
    action == Action::"api_call",
    resource == API::"any"
) when {
    context.origin not in [
        "https://app.example.com",
        "https://admin.example.com",
        "https://localhost:3000"
    ]
};

// File Upload Restrictions
permit(
    principal == User::"authenticated", 
    action == Action::"upload_file",
    resource == Storage::"user_files"
) when {
    resource.file_size < 10485760 && // 10MB
    resource.file_type in ["image/jpeg", "image/png", "application/pdf"] &&
    resource.scan_result == "clean"
};

// Database Access Controls
permit(
    principal == ServiceAccount::"application",
    action in [Action::"select", Action::"insert", Action::"update"],
    resource == Database::"application_db"
) when {
    resource.table not in ["admin_users", "audit_logs", "system_config"]
};

forbid(
    principal,
    action == Action::"drop_table",
    resource == Database::"any"
) when {
    principal.role != "database_admin"
};