kubectl delete -f manifests/deploy_app_serving.yaml
kubectl delete -f manifests/deploy_app_monitor.yaml
kubectl delete -f manifests/deploy_rbac.yaml
kubectl delete -f manifests/deploy_redis.yaml 
kubectl delete -f manifests/deploy_postgres.yaml