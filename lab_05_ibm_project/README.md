After completing the hands-on lab: Build and Deploy a Simple Guestbook App, you will complete the peer-graded assignment and be graded on the following ten tasks.

For each of the ten tasks, provide a screenshot and upload the JPEG (.jpg) file for your peers to review when you submit your work.

Task 1: Updation of the Dockerfile. (5 points)

Task 2: The guestbook image being pushed to IBM Cloud Container Registry correctly. (1 point)

Task 3: Index page of the deployed Guestbook – v1 application. (2 points)

Task 4: Horizontal Pod Autoscaler creation. (1 point)

Task 5: The replicas in the Horizontal Pod Autoscaler being scaled correctly. (2 points)

Task 6: The Docker build and push commmands for updating the guestbook.(2 points)

Task 7: Deployment configuration for autoscaling. (1 point)

Task 8: Updated index page of the deployed Guestbook – v2 application after rollout of the deployment. (2 points)

Task 9: The revision history for the deployment after rollout of the deployment. (2 points)

Task 10: The udpated deployment after Rollback of the update. (2 points)



# Results

```
(base) andrei@AID-MOB:~/work/ibm-k8s/k8s-ibm-base/lab_project/v1/guestbook$ ./test.sh 
New response: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-xg4pd)
New response: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-m5rsd)
New response: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-rczd6)
Sending request number 100 to http://localhost:30000/hello
Sending request number 200 to http://localhost:30000/hello
Sending request number 300 to http://localhost:30000/hello
Sending request number 400 to http://localhost:30000/hello
Sending request number 500 to http://localhost:30000/hello
Summary of responses:
Hostname: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-xg4pd) -> 170 responses
Hostname: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-rczd6) -> 165 responses
Hostname: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-m5rsd) -> 165 responses
Average time per request: .0052 seconds
(base) andrei@AID-MOB:~/work/ibm-k8s/k8s-ibm-base/lab_project/v1/guestbook$ ./test.sh 
New response: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-jh9lt)
Sending request number 100 to http://localhost:30000/hello
Sending request number 200 to http://localhost:30000/hello
Sending request number 300 to http://localhost:30000/hello
Sending request number 400 to http://localhost:30000/hello
Sending request number 500 to http://localhost:30000/hello
Summary of responses:
Hostname: Hello from guestbook. Your app is up! (Hostname: guestbook-6746559777-jh9lt) -> 500 responses
Average time per request: .0081 seconds
```

```bash
kubectl autoscale deployment guestbook --cpu-percent=5 --min=1 --max=10
```
after a while (autoscale warmup) we can see the following:
```bash
kubectl get hpa
kubectl get pods
```


### Another load approach
```bash
kubectl run -i --tty load-generator --rm --image=busybox:1.36.0 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- https://ionutdam-3000.theiaopenshift-0-labs-prod-theiaopenshift-4-tor01.proxy.cognitiveclass.ai/; done"
```


### Optional OpenShift

 1. Create an image stream that points to your image in IBM Cloud Container Registry.

```bash
oc tag us.icr.io/$MY_NAMESPACE/guestbook:v1 guestbook:v1 --reference-policy=local --scheduled
```
With the `--reference-policy=local`` option, a copy of the image from IBM Cloud Container Registry is imported into the local cache of the internal registry and made available to the cluster’s projects as an image stream. The `--schedule option`` sets up periodic importing of the image from IBM Cloud Container Registry into the internal registry. The default frequency is 15 minutes.
Here is the output:
```
Tag guestbook:v1 set to import us.icr.io/sn-labs-ionutdam/guestbook:v1 periodically.
```

 2. Create a deployment configuration that uses the image stream.

```bash