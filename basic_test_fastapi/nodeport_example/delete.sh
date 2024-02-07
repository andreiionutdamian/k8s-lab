APP_NAME="basic-test-py"
kubectl delete -f deploy_nodeport.yaml

# Wait for the pods to be deleted
while kubectl get pods -l run=$APP_NAME; do 
  echo "Waiting for pods to terminate..."
  sleep 5
done

echo "All pods terminated."