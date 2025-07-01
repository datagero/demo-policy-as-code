package cross.validation

# Helper: does this field exist in any schema column?
any_schema_column(f) if {
  some model in input.schema.models
  some col in model.columns
  col.name == f
}

input_debug := input

mapping_field_names := [k | k := object.get(input.mapping, "fields", {})[_]]

mapping_fields := [k | k := input.mapping.fields[_]]
schema_columns := [{"name": col.name, "role": col.column_security_role} | some model in input.schema.models; some col in model.columns]

# Debug: show what we're extracting
mapping_keys := [k | input.mapping.fields[k]]
schema_col_names := [col.name | some model in input.schema.models; some col in model.columns]

# Fail: present in both mapping and schema, but policy is missing
fail_missing := [
  {
    "field": f,
    "expected": input.mapping.fields[f].mask_policy,
    "actual": null
  } |
    f := mapping_keys[_]
    some model in input.schema.models
    some col in model.columns
    col.name == f
    not col.column_security_role
]

# Fail: present in both mapping and schema, but policy does not match
fail_mismatch := [
  {
    "field": f,
    "expected": input.mapping.fields[f].mask_policy,
    "actual": col.column_security_role
  } |
    f := mapping_keys[_]
    some model in input.schema.models
    some col in model.columns
    col.name == f
    col.column_security_role
    col.column_security_role != input.mapping.fields[f].mask_policy
]

mapping_debug := input.mapping
mapping_fields_debug := input.mapping.fields 