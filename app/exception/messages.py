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

    CURRENT_PASSWORD_INCORRECT = (
        "Current password is incorrect."
    )

    NEW_PASSWORD_SAME_AS_CURRENT = (
        "New password must be different from current password."
    )

    ADMIN_ROLE_NOT_CONFIGURED = (
        "ADMIN role is not configured."
    )

    PASSWORD_CHANGED_SUCCESSFULLY = (
        "Password changed successfully."
    )

    INVALID_REFRESH_TOKEN = (
        "Invalid or expired refresh token."
    )

    INVALID_TOKEN_TYPE = (
        "Invalid token type."
    )

    LOGOUT_SUCCESSFUL = (
        "Logout successful."
    )

class OrganizationMessages:
    SLUG_ALREADY_EXISTS = "Organization slug already exists."


class UserMessages:
    USER_NOT_FOUND = "User not found."



class ProjectMessages:
    PROJECT_NOT_FOUND = "Project not found"

    PROJECT_KEY_ALREADY_EXISTS = (
        "A project with this key already exists"
    )

    PROJECT_ALREADY_ACTIVE = (
        "Project is already active"
    )

    PROJECT_ALREADY_INACTIVE = (
        "Project is already inactive"
    )

    USER_NOT_FOUND = "User not found"

    MEMBER_ALREADY_EXISTS = (
        "User is already a member of this project"
    )

    PROJECT_MEMBER_NOT_FOUND = (
        "Project member not found"
    )

    INVALID_USER_ROLE = (
        "Invalid user role"
    )
    PERMISSION_DENIED = (
        "You do not have permission to perform this action"
    )


class TestCaseMessages:
    TEST_CASE_NOT_FOUND = "Test case not found."
    TAG_NOT_FOUND = "Tag not found."


class TestStepMessages:
    TEST_STEP_NOT_FOUND = "Test step not found."
    TEST_STEP_ALREADY_EXISTS = "Test step already exists."
    INVALID_STEP_NUMBER = "Invalid step number."
    INVALID_SORT_FIELD = "Invalid sort field."
    INVALID_REORDER = "Invalid step order."

class TestCycleMessages:
    TEST_CYCLE_NOT_FOUND = "Test cycle not found."
    INVALID_SORT_FIELD = "Invalid sort field."


class TestCycleMessages:
    TEST_CYCLE_NOT_FOUND = "Test cycle not found."
    INVALID_SORT_FIELD = "Invalid sort field."
    TEST_CASE_ALREADY_MAPPED = "Test case is already mapped to this cycle."
    TEST_CASE_NOT_MAPPED = "Test case is not mapped to this cycle."