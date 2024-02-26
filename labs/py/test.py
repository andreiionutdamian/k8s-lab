from kmonitor import KubeMonitor, safe_jsonify

if __name__ == '__main__':
  km = KubeMonitor()
  
  apps = ['emqx', 'nvidia', 'calico-node', 'basic-test']
  
  result = km.check_pods_by_names(apps)
  
  print(safe_jsonify(result, indent=2))