from kubernetes import client, config

def check_pod_state(namespace, pod_name):
    # Load the kubeconfig file
    config.load_kube_config()

    # Create an instance of the CoreV1Api
    v1 = client.CoreV1Api()

    try:
        # Fetch the specified pod
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)

        # Print the current status of the pod
        print(f"Pod {pod_name} in namespace {namespace} is currently in the {pod.status.phase} phase.")

        # Check if there are any conditions that provide additional details
        if pod.status.conditions:
            for condition in pod.status.conditions:
                print(f"Condition: {condition.type}, Status: {condition.status}, Reason: {condition.reason}")

        # Check the status of containers within the pod
        if pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                print(f"Container: {container_status.name}, Ready: {container_status.ready}, State: {container_status.state}")

    except client.exceptions.ApiException as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
  check_pod_state("kube-system", "calico-node-44m6t")
