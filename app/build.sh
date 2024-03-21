docker build -t aidamian/basic_test_fastapi -f Dockerfile_basic .
docker push aidamian/basic_test_fastapi

docker build -t aidamian/basic_serving_test_gpu -f Dockerfile_serving_gpu .
docker push aidamian/basic_serving_test_gpu

docker build -t aidamian/basic_serving_test_cpu -f Dockerfile_serving_cpu .
docker push aidamian/basic_serving_test_cpu

docker build -t aidamian/basic_cluster_monitor_test -f Dockerfile_monitor .
docker push aidamian/basic_cluster_monitor_test
