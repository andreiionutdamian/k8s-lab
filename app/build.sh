docker build -t aidamian/simple_test_fastapi -f Dockerfile_basic .
docker push aidamian/simple_test_fastapi

docker build -t aidamian/simple_serving_test_gpu -f Dockerfile_serving_gpu .
docker push aidamian/simple_serving_test_gpu

docker build -t aidamian/simple_serving_test_cpu -f Dockerfile_serving_cpu .
docker push aidamian/simple_serving_test_cpu

docker build -t aidamian/simple_cluster_monitor_test -f Dockerfile_monitor .
docker push aidamian/simple_cluster_monitor_test
