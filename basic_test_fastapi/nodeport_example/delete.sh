APP_NAME="basic-test-py"
NAMESPACE="basic-ns11"
kubectl delete -f deploy_nodeport.yaml

# Wait for the pods to be deleted
while kubectl get pods -l run=$APP_NAME -n $NAMESPACE; do 
  echo "Waiting for pods to terminate..."
  sleep 5
done

echo "All pods terminated."