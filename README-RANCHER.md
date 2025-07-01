# Running OPA Policy-as-Code in Rancher

This guide explains how to deploy and run the Open Policy Agent (OPA) project in Rancher instead of using Docker Compose.

## Prerequisites

- Rancher Desktop or Rancher Server with access to a Kubernetes cluster
- kubectl configured to access your cluster
- The Kubernetes manifests in the `k8s/` directory

## Deployment Options

### Option 1: Using kubectl (Command Line)

1. **Create the ConfigMap from your policy file:**
   ```bash
   kubectl create configmap opa-policies --from-file=access_policy.rego=access_policy.rego -n opa-policy
   ```

2. **Deploy the remaining Kubernetes resources:**
   ```bash
   kubectl apply -k k8s/
   ```

3. **Verify deployment:**
   ```bash
   kubectl get all -n opa-policy
   kubectl get pods -n opa-policy
   ```

4. **Access the service:**
   ```bash
   # Port forward to access locally
   kubectl port-forward -n opa-policy svc/opa-service 8181:8181
   ```

## Updating the OPA Policy

When you need to modify your policy rules, follow these steps:

### Step 1: Edit Your Policy File
```bash
# Edit the access_policy.rego file with your changes
# Example: Add new rules, modify existing logic, etc.
```

### Step 2: Recreate the ConfigMap
```bash
# Delete the existing ConfigMap
kubectl delete configmap opa-policies -n opa-policy

# Create a new ConfigMap from your updated file
kubectl create configmap opa-policies --from-file=access_policy.rego=access_policy.rego -n opa-policy
```

### Step 3: Restart the Deployment
```bash
# Restart the OPA deployment to pick up the new policy
kubectl rollout restart deployment/opa-server -n opa-policy
```

### Step 4: Verify the Update
```bash
# Check that the new pod is running
kubectl get pods -n opa-policy

# Check the logs to ensure no errors
kubectl logs -n opa-policy deployment/opa-server

# Test your updated policy
kubectl port-forward -n opa-policy svc/opa-service 8181:8181
# Then test with curl commands (see Testing section below)
```

### Quick Update Script
You can also create a simple script to automate the update process:

```bash
#!/bin/bash
# update-policy.sh
echo "Updating OPA policy..."

# Delete existing ConfigMap
kubectl delete configmap opa-policies -n opa-policy

# Create new ConfigMap from file
kubectl create configmap opa-policies --from-file=access_policy.rego=access_policy.rego -n opa-policy

# Restart deployment
kubectl rollout restart deployment/opa-server -n opa-policy

echo "Policy update complete! Check pod status with: kubectl get pods -n opa-policy"
```

Make it executable: `chmod +x update-policy.sh`
Then run: `./update-policy.sh`

## Testing the Deployment

Once deployed, you can test the OPA service:

1. **Port forward to access the service:**
   ```bash
   kubectl port-forward -n opa-policy svc/opa-service 8181:8181
   ```

2. **Test the API endpoints:**
   ```bash
   # Check if policies are loaded
   curl http://localhost:8181/v1/policies
   
   # Test with input data
   curl -X POST --data-binary @input.json \
     'http://localhost:8181/v1/data/example/allow_access' \
     -H 'Content-Type: application/json'
   ```

## Configuration

### Scaling

To scale the OPA service:

```bash
kubectl scale deployment opa-server --replicas=3 -n opa-policy
```

### Resource Limits

The deployment includes resource requests and limits:
- Memory: 64Mi request, 128Mi limit
- CPU: 50m request, 100m limit

Adjust these in `k8s/deployment.yaml` as needed.

## Cleanup

To remove the deployment:

```bash
kubectl delete configmap opa-policies -n opa-policy
kubectl delete -k k8s/
```

Or delete individual resources through the Rancher UI.

## Troubleshooting

1. **Check pod logs:**
   ```bash
   kubectl logs -n opa-policy deployment/opa-server
   ```

2. **Check pod status:**
   ```bash
   kubectl describe pod -n opa-policy -l app=opa-server
   ```

3. **Verify ConfigMap:**
   ```bash
   kubectl get configmap opa-policies -n opa-policy -o yaml
   ```

## Differences from Docker Compose

- **Persistence**: Policies are stored in ConfigMaps instead of mounted files
- **Scaling**: Can scale horizontally with multiple replicas
- **Networking**: Uses Kubernetes services and ingress instead of direct port mapping
- **Resource Management**: Includes resource requests and limits
- **High Availability**: Can be deployed across multiple nodes 