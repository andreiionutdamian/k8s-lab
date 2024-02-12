docker build -t aidamian/basic_test_fastapi -f Dockerfile_basic .
docker push aidamian/basic_test_fastapi

docker build -t aidamian/basic_cluster_serving_test -f Dockerfile_serving .
docker push aidamian/basic_cluster_serving_test

docker build -t aidamian/basic_cluster_monitor_test -f Dockerfile_monitor .
docker push aidamian/basic_cluster_monitor_test
