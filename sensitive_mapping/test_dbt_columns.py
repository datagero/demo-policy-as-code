import os
import warnings
import random
import sys
import yaml

from collections import defaultdict

import pandas as pd
from shared_test_functions import (
    abbreviation_ref,
    add_color,
    check_for_errors,
    check_string_is_abbreviation_or_full_word,
    combine_columns_into_one,
    format_error_message,
    get_singular_word_from_string,
    suggest_fix_for_word,
)

project_path = os.getenv('project_path', '')
cicd_path = os.getenv('cicd_path', '') + '/ref_files'

columns_audit_path = project_path + '/' + os.getenv('columns_path', 'seeds/olympus_dbt_audit_columns.csv')

if os.path.exists(columns_audit_path) is False:
    sys.exit(0)  # No columns file present

columns_audit = pd.read_csv(columns_audit_path)
# Below is the dbt standard columns exempt from the tests
dbt_standard_columns = [
    'dbt_scd_id',
    'dbt_updated_at',
    'dbt_valid_from',
    'dbt_valid_to',
    'value_var',
    'dcr_desc',
    'id',
    'value',
    'metadata_filename',
    'metadata_file_last_modified',
    'metadata_file_row_number',
    '_dbt_copied_at',
    'bus_eff_ts',
    'bus_exp_ts',
    'record_id',
    'sys_upd_ts',
]

columns_audit = columns_audit[
    (~columns_audit['column_name'].isin(dbt_standard_columns))
    & (columns_audit['model_type'].isin(['model']))  # Exclude external tables from tests
]

columns_audit.loc[:, 'skip_naming_validation'] = (columns_audit['column_tags'].fillna('').str.contains('skip_test')) | (
    columns_audit['column_tags'].fillna('').str.contains('skip_naming_validation')
)

with open(cicd_path + '/inspiration.txt') as file:
    inspirational_quote = file.readlines()

suffix_ref = pd.read_csv(cicd_path + '/suffixes.csv')
suggested_suffix_ref = pd.read_csv(cicd_path + '/suggested_suffixes.csv')
# abbreviation_ref = pd.read_csv(cicd_path + '/NamingStandards.txt', delimiter='|')
column_access_policy_ref = pd.read_csv(cicd_path + '/column_access_policy.csv')
pii_types_ref = pd.read_csv(cicd_path + '/pii_types.csv')
sensitive_data_types_ref = pd.read_csv(cicd_path + '/sensitive_data_types.csv')

suffixes = list(suffix_ref['Abbreviation'].sort_values(ascending=True))
column_access_policies = list(column_access_policy_ref['column_access_policy'].sort_values(ascending=True))
pii_types = list(pii_types_ref['type'].sort_values(ascending=True))
sensitive_data_types = list(sensitive_data_types_ref['type'].sort_values(ascending=True))

# Rsplit to ignore the suffix
columns_split = columns_audit['column_name'].str.rsplit('_', n=1).str[0].str.split('_', expand=True)
column_split_lenth = columns_split.shape[1]
columns_audit = pd.concat([columns_audit, columns_split], axis=1)

seperator_line_length = 40


def test_sensitive_fields_masking_policies():
    """
    Test that all sensitive columns defined in the mapping file are present in the DBT audit output
    and have the correct masking policy applied.

    Test logic:
    - For each sensitive column (from mapping file):
        - If the column is missing in the DBT audit, or if present but missing/null policy: **FAIL**
        - If the column exists in DBT but its policy mismatches mapping: **WARN (not fail)**
    - This ensures all sensitive fields are properly protected in the data warehouse.
    """

    # Load YAML mapping of sensitive fields and expected masking policies
    sensitive_fields_path = os.path.join(cicd_path, 'sensitive_fields_mapping.yml')
    if not os.path.exists(sensitive_fields_path):
        raise FileNotFoundError(f"Missing reference file: {sensitive_fields_path}")

    with open(sensitive_fields_path, 'r') as file:
        sensitive_fields_mapping = yaml.safe_load(file)

    # Sanity-check the YAML format
    if not isinstance(sensitive_fields_mapping, dict):
        raise ValueError("Invalid YAML format in sensitive_fields_mapping.yml")
    if 'fields' not in sensitive_fields_mapping:
        raise ValueError("YAML file must contain 'fields' key.")

    # Prepare a mapping: {column_name: expected_mask_policy}
    fields_mapping = sensitive_fields_mapping['fields']
    mapping_policies = {col: attrs.get('mask_policy') for col, attrs in fields_mapping.items()}

    # Prepare a lookup of actual DBT columns and their assigned security roles
    # This comes from the flattener CSV (columns_audit)
    audit_subset = columns_audit[['model_name', 'column_name', 'column_security_role']]

    # Allow multiple rows per column_name by model: column_name → [ {model_name, column_security_role}, ... ]
    dbt_columns = defaultdict(list)
    for _, row in audit_subset.iterrows():
        dbt_columns[row['column_name']].append({
            'model_name': row['model_name'],
            'column_security_role': row['column_security_role']
        })

    # Prepare containers for failed and warning cases
    errors = []
    mismatches = []

    # For each sensitive field in the mapping, check DBT enforcement
    for col, expected_policy in mapping_policies.items():
        dbt_infos = dbt_columns.get(col)

        if not dbt_infos:
            # Sensitive column missing from DBT audit = FAIL (not enforced in model)
            errors.append({
                'model_name': None,
                'column_name': col,
                'expected_policy': expected_policy,
                'actual_policy': None,
                'warning': (
                    f"Sensitive tag declared in mapping but not applied in DBT model. "
                    f"Suggest adding column_security_role: {expected_policy} to DBT model."
                )
            })
            continue

        # Evaluate each appearance of this sensitive column
        for dbt_info in dbt_infos:
            model_name = dbt_info['model_name']
            actual_policy = dbt_info['column_security_role']

            # Sensitive column present, but no security policy = FAIL
            if not actual_policy or pd.isna(actual_policy):
                errors.append({
                    'model_name': model_name,
                    'column_name': col,
                    'expected_policy': expected_policy,
                    'actual_policy': actual_policy or 'None',
                    'warning': (
                        f"Sensitive field present in DBT but has no column_security_role. "
                        f"Expected '{expected_policy}', got '{actual_policy or 'None'}'."
                    )
                })
            # Sensitive column present, policy differs from mapping = WARNING (not fail)
            elif actual_policy != expected_policy:
                mismatches.append({
                    'model_name': model_name,
                    'column_name': col,
                    'expected_policy': expected_policy,
                    'actual_policy': actual_policy,
                    'warning': (
                        f"Mismatch - Expected '{expected_policy}', got '{actual_policy}'. Manual override possible."
                    )
                })

    # Formatting constants for colors
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

    # Always print details for logging/traceability
    if mismatches:
        mismatch_df = pd.DataFrame(mismatches)
        mismatch_df['skip_naming_validation'] = False

        # Colorize each line of the mismatch table
        raw_table_lines = mismatch_df[
            ['model_name', 'column_name', 'expected_policy', 'actual_policy', 'skip_naming_validation']] \
            .to_string(index=False).split('\n')
        colored_table = "\n".join(f"{YELLOW}{line}" for line in raw_table_lines) + RESET

        # Colorize each detail row
        detailed_mismatches = "\n".join(
            f"{YELLOW} • {row['model_name']}.{row['column_name']}: {row['warning']}"
            for _, row in mismatch_df.iterrows()
        ) + RESET

        warnings.warn(
            f"\n{YELLOW}[WARNING] Sensitive field policy mismatches detected:\n"
            f"{colored_table}\n\n{YELLOW}[Details]\n{detailed_mismatches}",
            UserWarning
        )

    # Fail the test if any errors (missing or unenforced policies)
    if errors:
        error_df = pd.DataFrame(errors)
        error_df['skip_naming_validation'] = False
        error_table = error_df[['model_name', 'column_name', 'expected_policy', 'actual_policy', 'skip_naming_validation']].to_string(index=False)
        detailed_errors = "\n".join(
            f" • {row['model_name']}.{row['column_name']}: {row['warning']}"
            for _, row in error_df.iterrows()
        )

        error_msg = (
            f"\n{RED}[ERROR] Detected sensitive field(s) not enforced in DBT model:{RESET}\n"
            f"{error_table}\n\n[Details]\n{detailed_errors}"
        )

        assert False, error_msg

