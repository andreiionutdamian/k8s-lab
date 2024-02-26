from kubernetes import client, config

class KubernetesMetrics:
    """
    A class to fetch metrics from the Kubernetes Metrics API and convert them into more readable units.
    """
    def __init__(self):
        config.load_kube_config()
        self.custom_api = client.CustomObjectsApi()

    def get_node_metrics(self):
        """
        Fetches metrics for all nodes and converts them to readable units.

        Returns
        -------
        list
            A list of nodes with their CPU (in millicores) and memory usage (in GiB).
        """
        node_metrics = self.custom_api.list_cluster_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            plural="nodes"
        )
        metrics_list = []
        for node in node_metrics.get('items', []):
            cpu_usage_millicores = int(node['usage']['cpu'].rstrip('n')) / 1e6  # Convert nanocores to millicores
            memory_usage_gib = int(node['usage']['memory'].rstrip('Ki')) / (1024**2)  # Convert KiB to GiB
            metrics_list.append({
                'name': node['metadata']['name'],
                'cpu_usage_millicores': f"{cpu_usage_millicores:.2f} millicores",
                'memory_usage_gib': f"{memory_usage_gib:.2f} GiB"
            })
        return metrics_list

    def get_pod_metrics(self, namespace='default'):
        """
        Fetches metrics for all pods in a specified namespace and converts them to readable units.

        Parameters
        ----------
        namespace : str, optional
            The namespace to fetch pod metrics from (default is 'default').

        Returns
        -------
        list
            A list of pods with their CPU (in millicores) and memory usage (in GiB).
        """
        pod_metrics = self.custom_api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods"
        )
        metrics_list = []
        for pod in pod_metrics.get('items', []):
            containers_metrics = []
            for container in pod['containers']:
                cpu_usage_millicores = int(container['usage']['cpu'].rstrip('n')) / 1e6  # Convert nanocores to millicores
                memory_usage_gib = int(container['usage']['memory'].rstrip('Ki')) / (1024**2)  # Convert KiB to GiB
                containers_metrics.append({
                    'name': container['name'],
                    'cpu_usage_millicores': f"{cpu_usage_millicores:.2f} millicores",
                    'memory_usage_gib': f"{memory_usage_gib:.2f} GiB"
                })
            metrics_list.append({
                'pod_name': pod['metadata']['name'],
                'namespace': pod['metadata']['namespace'],
                'containers': containers_metrics
            })
        return metrics_list

# Example usage
if __name__ == "__main__":
    metrics = KubernetesMetrics()
    print("Node Metrics:")
    for node_metric in metrics.get_node_metrics():
        print(node_metric)

    print("\nPod Metrics in Default Namespace:")
    for pod_metric in metrics.get_pod_metrics():
        print(pod_metric)
