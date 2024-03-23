sudo nerdctl pull aidamian/simple_test_k8s
# sudo nerdctl run --rm --net=host -v /etc/kubernetes/admin.conf:/root/.kube/config aidamian/test_k8s
sudo nerdctl run --rm -v /etc/kubernetes/admin.conf:/root/.kube/config aidamian/simple_test_k8s
