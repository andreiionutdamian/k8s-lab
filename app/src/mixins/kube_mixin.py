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
    self.__v1apps = k8s.client.AppsV1Api()
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
    v1apps = self.__v1apps
    namespace = self.get_current_namespace()
    result["namespace"] = namespace
    result["pods"] = []
    result["deployments"] = []
    result["statefulsets"] = []
    if verbose: 
      self.P(f" Listing apps  in namespace '{namespace}':")
    try:
      ret = v1apps.list_namespaced_deployment(namespace=namespace)
      for i in ret.items:
        result["deployments"].append(i.metadata.name)
        if verbose:
          self.P(f"  {i.metadata.namespace}/{i.metadata.name}") 

      ret = v1apps.list_namespaced_stateful_set(namespace=namespace)
      for i in ret.items:
        result["statefulsets"].append(i.metadata.name)
        if verbose:
          self.P(f"  {i.metadata.namespace}/{i.metadata.name}") 
      
      ret = v1.list_namespaced_pod(namespace=namespace)
      for i in ret.items:
        result["pods"].append(i.metadata.name)
        if verbose:
          self.P(f"  {i.metadata.namespace}/{i.metadata.name}") 

    except ApiException as exc:
      self.__handle_exception(exc)
      result = f"Exception when calling Kubernetes API"
    return result
  
  def update_deployment(self, deployment_name: str, container_name:str, new_ver:str, check_ver:str = None ):
    result = None
    namespace = self.get_current_namespace()
    apps_v1_api = self.__v1apps
    try:
      deployment = apps_v1_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
      # Update the container image
      for container in deployment.spec.template.spec.containers:
        if container.name == container_name:
          image = container.image.split(":",1)
          image_name = image[0]
          image_tag = image[1] if len(image) > 1 else None

          if check_ver:
            self.P("Version checking...")
            if image_tag is None or  image_tag != check_ver:
              result = "Version mismatch"

          if result is None:
            container.image = image_name+":"+ new_ver
            # Apply the update
            self.P("Changing version...to "+ container.image)
            apps_v1_api.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
            result = f"Deployment {deployment_name} version changed to {new_ver}"

      if result is None:
        result = f"Deployment {deployment_name} not found"
    except ApiException as exc:
      self.__handle_exception(exc)
      result = f"Exception when calling Kubernetes API"
    return result
  
  def update_statefulset(self, sset_name: str, container_name:str, check_ver:str, new_ver:str):
    result = None
    namespace = self.get_current_namespace()
    apps_v1_api = self.__v1apps
    try:

      sset = apps_v1_api.read_namespaced_stateful_set(name=sset_name, namespace=namespace)
      for container in sset.spec.template.spec.containers:
        if container.name == container_name:
          image = container.image.split(":",1)
          image_name = image[0]
          image_tag = image[1] if len(image) > 1 else None

          if check_ver:
            self.P("Version checking...")
            if image_tag is None or  image_tag != check_ver:
              result = "Version mismatch"

          if result is None:
            container.image = image_name+":"+ new_ver
            # Apply the update
            self.P("Changing version...to "+ container.image)
            apps_v1_api.patch_namespaced_stateful_set(name=sset_name, namespace=namespace, body=sset)
            result = f"Statefulset {sset_name} version changed to {new_ver}"

      if result is None:
        result = f"Statefulset {sset_name} not found"
    except ApiException as exc:
      self.__handle_exception(exc)
    return result