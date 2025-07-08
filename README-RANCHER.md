# OPA Policy-as-Code on Rancher/Kubernetes

This guide shows how to quickly deploy Open Policy Agent (OPA) in Rancher/Kubernetes and test a simple policy.

## Prerequisites
- Rancher Desktop or a Kubernetes cluster
- kubectl configured

## 1. Deploy OPA and Policy

```bash
# Create namespace (if not exists)
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap with the example policy
kubectl create configmap opa-policies --from-file=access_policy.rego=policies/access_policy.rego -n opa-policy

# Deploy OPA and service
kubectl apply -k k8s/
```

## 2. (Optional) Install ConfigMap Reloader

```bash
./scripts/install-reloader.sh
```

## 3. Access OPA

```bash
# Use NodePort (default):
curl http://localhost:30081/v1/policies
```

## 4. Test the Example Policy

```bash
curl -X POST --data-binary @test_data/input.json \
  'http://localhost:30081/v1/data/example/allow_access' \
  -H 'Content-Type: application/json'
```

- `policies/access_policy.rego`:
  ```rego
  package example

  default allow_access = false

  allow_access if input.age >= 15
  ```
- `test_data/input.json`:
  ```json
  {
    "input": {
      "age": 16
    }
  }
  ```

## 5. Update Policy (Optional)

```bash
./scripts/update-policy.sh
```

---
For more advanced usage, see the main README. 