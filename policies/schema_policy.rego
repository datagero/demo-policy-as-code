package schema.validation

# Simple test rule
test_value := "schema policy loaded"

# Check if all security roles start with FOO_
all_roles_valid if {
    not exists_bad_role
}

exists_bad_role if {
    some model in input.schema.models
    some column in model.columns
    column.column_security_role
    not startswith(column.column_security_role, "FOO_")
}

# Find all columns with invalid security roles
invalid_roles := [
    {
        "model": model.name,
        "column": column.name,
        "invalid_role": column.column_security_role,
        "expected_prefix": "FOO_",
        "issue": "Security role does not start with FOO_"
    } |
    model := input.schema.models[_]
    column := model.columns[_]
    column.column_security_role
    not startswith(column.column_security_role, "FOO_")
]

# Find columns missing security roles (optional validation)
missing_roles := [
    {
        "model": model.name,
        "column": column.name,
        "issue": "No security role defined"
    } |
    model := input.schema.models[_]
    column := model.columns[_]
    not column.column_security_role
]

# Find columns with valid security roles
valid_roles := [
    {
        "model": model.name,
        "column": column.name,
        "security_role": column.column_security_role,
        "status": "valid"
    } |
    model := input.schema.models[_]
    column := model.columns[_]
    column.column_security_role
    startswith(column.column_security_role, "FOO_")
]

# Count total models and columns
total_models := count(input.schema.models)
total_columns := count([col | model := input.schema.models[_]; col := model.columns[_]])
sensitive_columns := count([col | model := input.schema.models[_]; col := model.columns[_]; col.column_security_role])

# Debug: show all columns OPA is seeing
debug_columns := [column | model := input.schema.models[_]; column := model.columns[_]]

# Summary of validation results
validation_summary := {
    "total_models": total_models,
    "total_columns": total_columns,
    "sensitive_columns": sensitive_columns,
    "valid_roles_count": count(valid_roles),
    "invalid_roles_count": count(invalid_roles),
    "missing_roles_count": count(missing_roles),
    "all_valid": all_roles_valid,
    "compliance_percentage": round((count(valid_roles) * 100) / sensitive_columns)
} 