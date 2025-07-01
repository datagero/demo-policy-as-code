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

# Count total models and columns
total_models := count(input.schema.models)
total_columns := count([col | model := input.schema.models[_]; col := model.columns[_]])
sensitive_columns := count([col | model := input.schema.models[_]; col := model.columns[_]; col.column_security_role]) 