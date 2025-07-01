#!/bin/bash

echo "Installing ConfigMap Reloader for automatic policy updates..."

# Add the stakater helm repository
helm repo add stakater https://stakater.github.io/stakater-charts
helm repo update

# Install the reloader
helm install reloader stakater/reloader \
  --namespace opa-policy \
  --create-namespace \
  --set reloader.watchGlobally=false

echo "ConfigMap Reloader installed!"
echo "Now when you update the ConfigMap, the OPA deployment will automatically restart."
echo ""
echo "To update your policy, just run:"
echo "kubectl create configmap opa-policies --from-file=access_policy.rego=access_policy.rego -n opa-policy --dry-run=client -o yaml | kubectl apply -f -" 