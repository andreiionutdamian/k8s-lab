from k8s_monitor.src.kmonitor.base import KubeMonitor, safe_jsonify

if __name__ == '__main__':
  km = KubeMonitor()
  
  # apps = ['emqx', 'nvidia', 'basic-test']
  
  # result = km.check_pods_by_names(apps)  
  # print("Pods {}:\n{}".format(apps, safe_jsonify(result, indent=2)))
  
  # nodes = km.get_nodes_metrics()
  # print("Nodes:\n{}".format(safe_jsonify(nodes, indent=2)))
  summary = km.summary()
  NP = 3
  result = {
    'namespaces': summary['namespaces'],
    'nodes': summary['nodes'],
    f'pods-first-{NP}': summary['pods'][:NP]
  }
  print("Summary:\n{}".format(safe_jsonify(result, indent=2)))
  