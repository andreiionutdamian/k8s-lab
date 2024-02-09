source utils.sh
log_with_color "Deleting all resources in namespace basic-ns11" "green"
./deploy1_nodeport/delete.sh
log_with_color "Deleting all resources in namespace basic-ns12" "green"
./deploy2_ingress/delete.sh
log_with_color "Deleting all resources in namespace basic-postgres" "green"
./deploy3_postgres/delete.sh
log_with_color "Deleting all resources in namespace basic-clusters" "green"
./deploy4_clusters/delete.sh
