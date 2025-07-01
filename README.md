# Policy-as-Code with Open Policy Agent (OPA)

This project implements data governance validation using Open Policy Agent (OPA) in Kubernetes, with policies for cross-validating sensitive field mappings and data product schemas.

## Project Structure

```
policy-as-code/
├── policies/                    # OPA Rego policy files
│   ├── access_policy.rego
│   ├── governance_policy.rego
│   ├── schema_policy.rego
│   └── cross_validation_policy.rego
├── test_data/                   # Test input files
│   ├── input.json
│   ├── test_cross_validation_input.json
│   ├── test_governance_input.json
│   └── test_schema_input.json
├── scripts/                     # Utility scripts
│   ├── update-policy.sh
│   ├── port-forward.sh
│   └── install-reloader.sh
├── k8s/                        # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── namespace.yaml
│   ├── nodeport-service.yaml
│   └── kustomization.yaml
├── sensitive_mapping/           # DBT models and sensitive field mappings
│   ├── dbt_model/
│   ├── schema_for_opa.json
│   ├── sensitive_fields_mapping.yml
│   └── simple_schema_generator.py
└── README.md
```

## Quick Start

1. **Deploy OPA to Kubernetes:**
   ```bash
   kubectl apply -k k8s/
   ```

2. **Install ConfigMap Reloader (for automatic policy updates):**
   ```bash
   ./scripts/install-reloader.sh
   ```

3. **Start port forwarding:**
   ```bash
   ./scripts/port-forward.sh
   ```

4. **Update policies:**
   ```bash
   ./scripts/update-policy.sh
   ```

5. **Test policies:**
   ```bash
   # Test cross-validation
   curl -X POST --data-binary @test_data/test_cross_validation_input.json \
     'http://localhost:30081/v1/data/cross/validation/fail_missing'
   ```

## Policy Types

### 1. Cross-Validation Policy (`cross_validation_policy.rego`)
Validates that schema columns match governance mappings:
- **fail_missing**: Fields present in mapping but missing `column_security_role` in schema
- **fail_mismatch**: Fields present in both but with mismatched security policies

### 2. Governance Policy (`governance_policy.rego`)
Validates governance mapping file structure and content.

### 3. Schema Policy (`schema_policy.rego`)
Validates data product schema structure and requirements.

### 4. Access Policy (`access_policy.rego`)
Defines access control rules for data resources.

## Testing

Use the test files in `test_data/` to validate your policies:

- `test_cross_validation_input.json`: Tests cross-validation scenarios
- `test_governance_input.json`: Tests governance policy validation
- `test_schema_input.json`: Tests schema validation

## Development

When modifying policies:
1. Edit files in `policies/`
2. Run `./scripts/update-policy.sh` to deploy changes
3. Test with appropriate files in `test_data/`

The ConfigMap Reloader will automatically restart the OPA deployment when policies are updated. 