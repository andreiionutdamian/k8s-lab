# get pods starting with demo-ai-app-monitor then log the first pod
kubectl logs $(kubectl get pods -n hwal | grep ai-app-mon | awk '{print $1}' | head -n 1) -n hwal
