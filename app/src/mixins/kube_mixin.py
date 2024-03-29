import json
try:
  import kubernetes as k8s
  from kubernetes.client.exceptions import ApiException  
  KUBE_AVAIL = True
except:
  KUBE_AVAIL = False
  
  
class _KubeMixin(object):
  def __init__(self):
    super(_KubeMixin, self).__init__()
    
    self._has_kube = KUBE_AVAIL
    if KUBE_AVAIL:
      self.__setup_kube()
    else:
      self.P("K8s api not working: kubernetes package not available")
    return
  
  def __handle_exception(self, exc):
    error_message = f"Exception when calling Kubernetes API."
    error_message += f" Reason: {exc.reason},"
    error_message += f" Status: {exc.status},"
    
    # Attempting to parse the body as JSON to extract detailed API response
    if exc.body:
      try:
        body = json.loads(exc.body)
        message = body.get("message")
        error_message += f"  Message: {message}"
      except json.JSONDecodeError:
        error_message += f"  Raw Body: {exc.body}"
      #end try
    #end if  
    self.P(error_message)    
    return
  
   
  def __setup_kube(self):
    self.P("Initializing k8s checker...")
    try:
        # Try to load in-cluster config first
      k8s.config.load_incluster_config()
      self.in_cluster = True
      self.P("  Running inside a Kubernetes cluster.")
    except k8s.config.ConfigException:
      # Fall back to kubeconfig (outside of cluster)
      k8s.config.load_kube_config()
      self.P("  Running outside a Kubernetes cluster.")
    
    self.__v1 = k8s.client.CoreV1Api()
    self.P("  K8s helper initialized. Checking namepace pods...")
    self.get_namespace_info()
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

  def get_namespace_info(self, verbose=False):
    result = {}
    # Now you can use the API, for example, list all pods in the current namespace
    v1 = self.__v1
    namespace = self.get_current_namespace()
    result["namespace"] = namespace
    result["pods"] = []
    if verbose: 
      self.P(f"Listing pods in namespace '{namespace}':")
    try:
      ret = v1.list_namespaced_pod(namespace=namespace)
      for i in ret.items:
        result["pods"].append(i.metadata.name)
        if verbose:
          self.P(f"  {i.metadata.namespace}/{i.metadata.name}")    
    except ApiException as exc:
      self.__handle_exception(exc)
    return result