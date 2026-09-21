# app/core/messages.py

class Messages:
    # Authentication
    INVALID_CREDENTIALS = "Invalid email or password."
    UNAUTHORIZED = "Authentication required."
    FORBIDDEN = "You do not have permission to perform this action."
    TOKEN_EXPIRED = "Token has expired."
    INVALID_TOKEN = "Invalid token."

    # Users
    USER_NOT_FOUND = "User not found."
    USER_ALREADY_EXISTS = "User already exists."

    # Organization
    ORGANIZATION_NOT_FOUND = "Organization not found."
    ORGANIZATION_ALREADY_EXISTS = "Organization already exists."

    # Projects
    PROJECT_NOT_FOUND = "Project not found."
    PROJECT_ALREADY_EXISTS = "Project already exists."
    PROJECT_ARCHIVED = "Project is archived."

    # Project Members
    PROJECT_MEMBER_NOT_FOUND = "Project member not found."
    PROJECT_MEMBER_ALREADY_EXISTS = "User is already a member of this project."

    # General
    INVALID_REQUEST = "Invalid request."
    RESOURCE_NOT_FOUND = "Resource not found."
    INTERNAL_SERVER_ERROR = "Internal server error."

class AuthMessages:
    INVALID_CREDENTIALS = "Invalid email or password."
    USER_INACTIVE = "User account is inactive."
    ORGANIZATION_INACTIVE = "Organization is inactive."
    CURRENT_PASSWORD_INCORRECT = "Current password is incorrect."
    NEW_PASSWORD_SAME_AS_CURRENT = (
        "New password must be different from current password."
    )
    ADMIN_ROLE_NOT_CONFIGURED = "ADMIN role is not configured."


class OrganizationMessages:
    SLUG_ALREADY_EXISTS = "Organization slug already exists."


class UserMessages:
    USER_NOT_FOUND = "User not found."