import numpy as np
from monitor.lib.kubemon import KubeMonitor, safe_jsonify


if __name__ == '__main__':
  km = KubeMonitor()
  pods = km.list_pods()
  if pods is not None:
    for pod in pods:
      print(f"Pod: {pod.metadata.name} in namespace {pod.metadata.namespace} is in phase {pod.status.phase}")
  else:
    print("Failed to get pods")

  namespaces = km.list_namespaces()
  if namespaces is not None:
    for ns in namespaces:
      print(f"Namespace: {ns.metadata.name}")
  else:
    print("Failed to get namespaces")
  
  nr_pods = len(pods)
  idx = np.random.randint(0, nr_pods)
  example_pod_name = "basic-test" # pods[idx].metadata.name
  print("Checking pod status for pod {}".format(example_pod_name))
  status = km.check_pod_by_name(example_pod_name)
  print(safe_jsonify(status, indent=2))

  example_pod_names = ["nvidia", "calico-node", "emqx"]
  print("Checking pod status for pods {}".format(example_pod_names))
  status = km.check_pods_by_names(example_pod_names)
  print(safe_jsonify(status, indent=2))
  
  
