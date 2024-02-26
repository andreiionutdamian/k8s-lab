from kmonitor import KubeMonitor, safe_jsonify

if __name__ == '__main__':
  km = KubeMonitor()
  
  apps = ['emqx', 'nvidia', 'basic-test']
  
  result = km.check_pods_by_names(apps)  
  print(safe_jsonify(result, indent=2))
  
  nodes = km.get_nodes_metrics()
  print(safe_jsonify(nodes, indent=2))
  