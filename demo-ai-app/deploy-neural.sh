kubectl apply -f manifests/storage-neural.yaml
kubectl apply -f manifests/deploy_postgres.yaml 
kubectl apply -f manifests/deploy_redis.yaml 
kubectl apply -f manifests/deploy_app_monitor.yaml
kubectl apply -f manifests/deploy_app_serving.yaml