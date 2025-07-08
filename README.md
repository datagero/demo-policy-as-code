# Policy-as-Code for Data Governance

This project enables organizations to automate and enforce data governance rules using Open Policy Agent (OPA) in Kubernetes. It allows you to define, test, and deploy policies as code, ensuring compliance and transparency for sensitive data workflows.

## Why Use This Project?
- **Automate data access controls** and governance checks
- **Reduce manual review** and human error
- **Easily update and test policies** as your business evolves
- **Integrate with Kubernetes** for scalable, cloud-native deployments
- **Cross-validate** governance mappings against data product schemas
- **Ensure compliance** with data security policies

## Quick Start (Local or Kubernetes)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd policy-as-code
   ```

2. **Deploy OPA and example policy to Kubernetes:**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl create configmap opa-policies --from-file=access_policy.rego=policies/access_policy.rego -n opa-policy
   kubectl apply -k k8s/
   ./scripts/install-reloader.sh   # Optional: for auto-reloading policies
   ```

3. **Test the policy:**
   ```bash
   curl -X POST --data-binary @test_data/input.json \
     'http://localhost:30081/v1/data/example/allow_access' \
     -H 'Content-Type: application/json'
   ```
   You should see a response indicating access is allowed or denied based on the input.

## Policy Types and Validation

### 1. Cross-Validation Policy
Validates that data product schemas comply with governance mappings:

```bash
# Test cross-validation scenarios
curl -X POST --data-binary @test_data/test_cross_validation_input.json \
  'http://localhost:30081/v1/data/cross/validation/fail_missing' \
  -H 'Content-Type: application/json'
```

**Scenarios:**
- **fail_missing**: Fields in governance mapping but missing security roles in schema
- **fail_mismatch**: Fields with mismatched security policies between mapping and schema

### 2. Governance Policy
Validates governance mapping file structure and content:

```bash
# Test governance validation
curl -X POST --data-binary @test_data/test_governance_input.json \
  'http://localhost:30081/v1/data/governance/validation/all_policies_valid' \
  -H 'Content-Type: application/json'
```

**Checks:**
- All mask policies follow naming conventions (e.g., start with "FOO_")
- Required fields are present in the mapping

### 3. Schema Policy
Validates data product schema structure and requirements:

```bash
# Test schema validation
curl -X POST --data-binary @test_data/test_schema_input.json \
  'http://localhost:30081/v1/data/schema/validation/all_roles_valid' \
  -H 'Content-Type: application/json'
```

**Checks:**
- All security roles follow naming conventions
- Required schema structure is maintained

## Updating Policies

1. **Edit policy files** in the `policies/` directory
2. **Deploy changes:**
   ```bash
   ./scripts/update-policy.sh
   ```
3. **Test your changes** using the appropriate test files in `test_data/`

The ConfigMap Reloader automatically restarts OPA when policies are updated, ensuring zero downtime.

## Project Structure

```
policy-as-code/
├── policies/        # OPA policy files (.rego)
├── test_data/       # Example input files
├── scripts/         # Helper scripts
├── k8s/             # Kubernetes manifests
└── README.md
```

## Need Rancher/Kubernetes Setup?
See [README-RANCHER.md](README-RANCHER.md) for step-by-step Rancher/K8s deployment instructions. 