#!/bin/bash

echo "Updating OPA policies..."

# Update ConfigMap using kubectl apply (seamless with reloader)
kubectl create configmap opa-policies \
  --from-file=access_policy.rego=access_policy.rego \
  --from-file=governance_policy.rego=governance_policy.rego \
  --from-file=schema_policy.rego=schema_policy.rego \
  --from-file=cross_validation_policy.rego=cross_validation_policy.rego \
  -n opa-policy --dry-run=client -o yaml | kubectl apply -f -

echo "Policy update complete!"
echo "The ConfigMap Reloader will automatically restart the OPA deployment."
echo "Check pod status with: kubectl get pods -n opa-policy" 