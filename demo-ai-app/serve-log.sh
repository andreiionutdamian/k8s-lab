# get parameter from cli else use 0
if [ -z "$1" ]; then
  NODE_ID=0
else
  NODE_ID=$1
fi
kubectl logs ai-app-serve-$NODE_ID -n hwal