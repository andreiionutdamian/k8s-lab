# get pods starting with demo-ai-app-monitor then log the first pod
kubectl logs $(kubectl get pods -n hwal | grep demo-ai-app-monitor | awk '{print $1}' | head -n 1) -n hwal
