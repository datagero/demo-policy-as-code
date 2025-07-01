package governance.validation

# Simple test rule
test_value := "governance policy loaded"

# Check if all mask policies start with FOO_
all_policies_valid if {
    not exists_bad_policy
}

exists_bad_policy if {
    some field_name, field_data in input.mapping.fields
    not startswith(field_data.mask_policy, "FOO_")
}

# Count total fields
total_fields := count(input.mapping.fields) 