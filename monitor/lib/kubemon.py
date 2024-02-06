from datetime import datetime
from kubernetes import client, config


class KubeMonitor:
  def __init__(self, log=None):
    self.log = log
    self.__initialize()
    return
    
  def P(self, s, **kwargs):
    if self.log is not None:
      self.log.P(s, **kwargs)
    print(s, flush=True, **kwargs)
    
  def __initialize(self):
    # no try-except here. let the caller handle the exception or fail if it occurs
    config.load_kube_config()    
    self.__v1 = client.CoreV1Api()  
    return
    

  def list_pods(self):
    try:
      ret = self.__v1.list_pod_for_all_namespaces(watch=False)
    except Exception as exc:
      self.P(f"Exception while getting pods: {exc}")
      return None
    return ret.items


  def list_namespaces(self):
    try:
      ret = self.__v1.list_namespace(watch=False)
    except Exception as exc:
      self.P(f"Exception while getting namespaces: {exc}")
      return None
    return ret.items
  

  def _check_pod_health(self, pod):
    try:
      # Fetch the specified pod      
      health_status = {"status": "Success", "messages": []}

      # Determine if the pod is in a loading or initializing state
      if pod.status.phase in ["Pending"]:
        initializing_status = False
        for condition in pod.status.conditions or []:
          if condition.type == "PodScheduled" and condition.status != "True":
            health_status["status"] = "Loading"
            health_status["messages"].append("Pod is scheduled but not running yet.")
            initializing_status = True
          elif condition.type in ["Initialized", "ContainersReady"] and condition.status != "True":
            health_status["status"] = "Initializing"
            health_status["messages"].append(f"Pod is initializing: {condition.type} is {condition.status}.")
            initializing_status = True

        if not initializing_status:
          # If the pod is pending but no specific initializing status was detected,
          # it could be waiting for resources or other conditions.
          health_status["status"] = "Loading"
          health_status["messages"].append("Pod is pending, waiting for resources or other conditions.")

      elif pod.status.phase not in ["Running", "Succeeded"]:
        health_status["status"] = "Critical"
        health_status["messages"].append(f"Pod is in {pod.status.phase} phase.")

      # Check container statuses if pod phase is Running
      if pod.status.phase == "Running":
        health_status["containers"] = {}
        for container_status in pod.status.container_statuses or []:
          container_name = container_status.name
          dct_container = {}
          if not container_status.ready:
            health_status["status"] = "Warning"
            health_status["messages"].append(f"Container {container_status.name} is not ready.")
          if container_status.restart_count > 0:
            health_status["status"] = "Warning"
            health_status["messages"].append(f"Container {container_status.name} restarted {container_status.restart_count} times.")
          # now compute running time for this pod containers                   
          run_info = container_status.state.running                  
          running_time = (datetime.now(run_info.started_at.tzinfo) - run_info.started_at).total_seconds()
          hours, rem = divmod(running_time, 3600)
          minutes, seconds = divmod(rem, 60)
          # format elapsed time as a string        
          dct_container["started"] = run_info.started_at.strftime("%Y-%m-%d %H:%M:%S")
          dct_container["running_time"] = "{:0>2}:{:0>2}:{:0>2}".format(int(hours),int(minutes),int(seconds))
          if running_time > 3600:
            health_status["status"] = "Low warning"
            health_status["messages"].append(f"Container {container_status.name} has been running for {dct_container['running_time']}.")
          health_status["containers"][container_name] = dct_container
          

    except client.exceptions.ApiException as e:
      print(f"An error occurred: {e}")
      health_status = {"status": "Error", "messages": [str(e)]}
    
    return health_status
  
  def check_pod(self, namespace, pod_name):
    try:
      pod = self.__v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    except Exception as exc:
      self.P(f"Exception while getting pod {pod_name} in namespace {namespace}: {exc}")
      return None
    return self._check_pod_health(pod)
  
  def check_pod_by_name(self, pod_name):    
    pods = self.list_pods()
    if pods is None:
      health_status = {"status": "Error", "messages": ["Unable to get pods"]}
    else:      
      found = None
      for p in pods:
        if p.metadata.name == pod_name:
          found = p
          break        
      if found is None:
        health_status = {"status": "Error", "messages": [f"Pod {pod_name} not found"]}
      else:
        health_status = self._check_pod_health(found)
      #end if found
    #end if pods listed
    return health_status
    
    
    
    
    
    