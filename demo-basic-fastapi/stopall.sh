source ./utils.sh
log_with_color "Deleting all resources in namespace basic-ns11" green
cd ./deploy1_nodeport
./delete.sh
cd ..
log_with_color "Deleting all resources in namespace basic-ns12" green
cd ./deploy2_ingress/
./delete.sh
cd ..
log_with_color "Deleting all resources in namespace basic-postgres" green
cd ./deploy3_postgres/
./delete.sh
cd ..
log_with_color "Deleting all resources in namespace basic-clusters" green
cd ./deploy4_clusters
./delete.sh
cd ..
