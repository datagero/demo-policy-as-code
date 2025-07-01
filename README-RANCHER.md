# Running OPA Policy-as-Code in Rancher

This guide explains how to deploy and run the Open Policy Agent (OPA) project in Rancher instead of using Docker Compose.

## Prerequisites

- Rancher Desktop or Rancher Server with access to a Kubernetes cluster
- kubectl configured to access your cluster
- The Kubernetes manifests in the `k8s/` directory
- Helm (for installing the ConfigMap Reloader)

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

3. **Install ConfigMap Reloader for seamless updates:**
   ```bash
   chmod +x install-reloader.sh
   ./install-reloader.sh
   ```

4. **Verify deployment:**
   ```bash
   kubectl get all -n opa-policy
   kubectl get pods -n opa-policy
   ```

5. **Access the service:**
   ```bash
   # Port forward to access locally
   kubectl port-forward -n opa-policy svc/opa-service 8181:8181
   ```

## Updating the OPA Policy (Seamless)

With the ConfigMap Reloader installed, policy updates are now **automatic** - no manual restarts needed!

### Method 1: Using the Update Script (Recommended)
```bash
chmod +x update-policy.sh
./update-policy.sh
```

### Method 2: Manual Update
```bash
# Update the ConfigMap - the reloader will automatically restart the deployment
kubectl create configmap opa-policies --from-file=access_policy.rego=access_policy.rego -n opa-policy --dry-run=client -o yaml | kubectl apply -f -
```

### What Happens Automatically:
1. ✅ **ConfigMap updates** - your policy changes are applied
2. ✅ **Deployment restarts** - ConfigMap Reloader detects the change
3. ✅ **New pod starts** - with your updated policy
4. ✅ **Zero downtime** - seamless policy updates

### Verify the Update:
```bash
# Check that the new pod is running
kubectl get pods -n opa-policy

# Check the logs to ensure no errors
kubectl logs -n opa-policy deployment/opa-server

# Test your updated policy
kubectl port-forward -n opa-policy svc/opa-service 8181:8181
```

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
# Remove the reloader
helm uninstall reloader -n opa-policy

# Remove the deployment
kubectl delete configmap opa-policies -n opa-policy
kubectl delete -k k8s/
```

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

4. **Check reloader status:**
   ```bash
   kubectl get pods -n opa-policy -l app=reloader
   ```

## Differences from Docker Compose

- **Persistence**: Policies are stored in ConfigMaps instead of mounted files
- **Scaling**: Can scale horizontally with multiple replicas
- **Networking**: Uses Kubernetes services and ingress instead of direct port mapping
- **Resource Management**: Includes resource requests and limits
- **High Availability**: Can be deployed across multiple nodes
- **Seamless Updates**: Automatic policy reloading with ConfigMap Reloader 