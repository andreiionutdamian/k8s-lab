source ./utils.sh
log_with_color "Checking all resources in namespace basic-ns11" "green"
kubectl get all -n basic-ns11
log_with_color "Checking all resources in namespace basic-ns12" "green"
kubectl get all -n basic-ns12
log_with_color "Checking all resources in namespace basic-postres" "green"
kubectl get all -n basic-postgres
log_with_color "Checking all resources in namespace basic-clusters" "green"
kubectl get all -n basic-clusters