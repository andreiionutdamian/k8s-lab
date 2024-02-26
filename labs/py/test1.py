import json
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class ClusterHealthChecker:
  """
  A wrapper class around Kubernetes Python client for cluster health checking.

  Attributes
  ----------
  None

  Methods
  -------
  get_all_nodes():
      Retrieves all nodes in the cluster along with their status.

  get_node_load(node_name):
      Retrieves load information for a specific node.
  """
  def __init__(self):
    # Load kubeconfig and initialize the API client
    config.load_kube_config()
    self.v1 = client.CoreV1Api()

  def get_all_nodes(self):
    """
    Retrieves all nodes in the cluster along with their status.

    Returns
    -------
    list
        A list of nodes and their statuses.
    """
    try:
      nodes = self.v1.list_node()
      node_info = []
      for node in nodes.items:
        conditions = {condition.type: condition.status for condition in node.status.conditions}
        node_info.append({
          'name': node.metadata.name,
          'status': 'Ready' if conditions.get('Ready') == 'True' else 'Not Ready',
          'conditions': conditions
        })
      return node_info
    except ApiException as e:
      print(f"An exception occurred: {e}")
      return []

  def get_node_load(self, node_name):
    """
    Retrieves load information for a specific node.

    Parameters
    ----------
    node_name : str
        The name of the node to retrieve load information for.

    Returns
    -------
    dict
        A dictionary containing load information of the specified node.
    """
    try:
      node_details = self.v1.read_node_status(node_name, pretty=True) 
      return node_details
    except ApiException as e:
      print(f"An exception occurred: {e}")
      return {}

# Example usage
if __name__ == "__main__":
    checker = ClusterHealthChecker()
    nodes = checker.get_all_nodes()
    print("All nodes and their status:\n{}".format(json.dumps(nodes, indent=2)))
    node1 = nodes[0]['name']
    details = checker.get_node_load(node1)
    print(f"Details for node {node1}:\n{json.dumps(details, indent=2)}")
