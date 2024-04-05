docker build -t aidamian/simple_test_fastapi -f Dockerfile_basic .
docker push aidamian/simple_test_fastapi

serving_ver=${yq -e ".application.serving.version" ./demo-ai-app/manifests/version.yaml}
docker build -t aidamian/simple_serving_test_gpu:${serving_ver} -f Dockerfile_serving_gpu .
docker push aidamian/simple_serving_test_gpu:${serving_ver}

docker build -t aidamian/simple_serving_test_cpu:${serving_ver} -f Dockerfile_serving_cpu .
docker push aidamian/simple_serving_test_cpu:${serving_ver}

monitor_ver=${yq -e ".application.monitor.version" ./demo-ai-app/manifests/version.yaml}
docker build -t aidamian/simple_cluster_monitor_test:${monitor_ver} -f Dockerfile_monitor .
docker push aidamian/simple_cluster_monitor_test:${monitor_ver}
