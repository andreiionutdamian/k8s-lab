try:
  import kubernetes as k8s
  KUBE_AVAIL = True
except:
  KUBE_AVAIL = False
  
  
class _KubeMixin:
  def __init__(self, **kwargs):
    super(_KubeMixin, self).__init__(**kwargs)
    self._has_kube = KUBE_AVAIL
    if KUBE_AVAIL:
      self.__setup_kube()
    else:
      self.P("K8s api not working: kubernetes package not available")
    return
  
   
  def __setup_kube(self):
    self.P("Initializing k8s checker...")
    try:
        # Try to load in-cluster config first
      k8s.config.load_incluster_config()
      self.in_cluster = True
      self.P("Running inside a Kubernetes cluster.")
    except k8s.config.ConfigException:
      # Fall back to kubeconfig (outside of cluster)
      k8s.config.load_kube_config()
      self.P("Running outside a Kubernetes cluster.")
    
    self.__v1 = k8s.client.CoreV1Api()
    self.P("KubeMonitor initialized")    
    self._check_namespace()
    return
  
  def get_current_namespace(self):
    """
    Get the current namespace where this code is running.
    
    Returns
    -------
    str
        The current namespace.
    """
    try:
      with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
        return f.read().strip()
    except IOError:
      self.P("Could not read namespace, defaulting to 'default'")
      return "default"  

  def _check_namespace(self):
    # Now you can use the API, for example, list all pods in the current namespace
    v1 = self.__v1
    namespace = self.get_current_namespace()
    self.P(f"Listing pods in namespace '{namespace}'")
    ret = v1.list_namespaced_pod(namespace=namespace)
    for i in ret.items:
        self.P(f"  {i.metadata.namespace}/{i.metadata.name}")    