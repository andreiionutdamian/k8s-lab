kubectl logs $(kubectl get pods -n ne | grep ne-bot | awk '{print $1}' | head -n 1) -n ne