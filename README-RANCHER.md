# Running OPA Policy-as-Code in Rancher

This guide explains how to deploy and run the Open Policy Agent (OPA) project in Rancher instead of using Docker Compose.

## Prerequisites

- Rancher Desktop or Rancher Server with access to a Kubernetes cluster
- kubectl configured to access your cluster
- The Kubernetes manifests in the `k8s/` directory

## Deployment Options

### Option 1: Using kubectl (Command Line)

1. **Deploy to Kubernetes cluster:**
   ```bash
   kubectl apply -k k8s/
   ```

2. **Verify deployment:**
   ```bash
   kubectl get all -n opa-policy
   kubectl get pods -n opa-policy
   ```

3. **Access the service:**
   ```bash
   # Port forward to access locally
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

### Updating Policies

To update the OPA policies:

1. **Edit the ConfigMap:**
   ```bash
   kubectl edit configmap opa-policies -n opa-policy
   ```

2. **Restart the deployment:**
   ```bash
   kubectl rollout restart deployment/opa-server -n opa-policy
   ```

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