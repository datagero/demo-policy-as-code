#!/bin/bash

echo "Starting persistent port-forward to OPA service..."
echo "This will automatically reconnect if the connection drops."
echo "Press Ctrl+C to stop."
echo ""

while true; do
    echo "Connecting to OPA service on localhost:8181..."
    kubectl port-forward -n opa-policy svc/opa-service 8181:8181
    
    # If we get here, the connection dropped
    echo ""
    echo "Connection dropped. Reconnecting in 2 seconds..."
    sleep 2
done 