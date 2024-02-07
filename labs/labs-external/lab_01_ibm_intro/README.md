# Workshop 1 - Basics

1. From base folder `..` run `[ ! -d 'CC201' ] && git clone https://github.com/ibm-developer-skills-network/CC201.git` or just use the following scripts

```Dockerfile
FROM node:9.4.0-alpine
COPY app.js .
COPY package.json .
RUN npm install &&\
    apk update &&\
    apk upgrade
EXPOSE  8080
CMD node app.js
```

and

```javascript
var express = require('express')
var os = require("os");
var hostname = os.hostname();
var app = express()

app.get('/', function(req, res) {
  res.send('Hello world from ' + hostname + '! Your app is up and running!\n')
})
app.listen(8080, function() {
  console.log('Sample app is listening on port 8080.')
})
```

and finally `package.json`

```json
{
  "name": "hello-world-demo",
  "private": false,
  "version": "0.0.1",
  "description": "Basic hello world application for Node.js",
  "dependencies": {
    "express": "4.x"
  }
}

```


2. Goto `~/work/ibm-k8s/CC201/labs/2_IntroKubernetes` and lets get started

3. `kubectl config get-clusters` - this will show the clusters you have access to

4. `kubectl config get-contexts` - this will show the contexts you have access to (ccess parameters, including a cluster, a user, and a namespace)

5. `kubectl get pods` - this will show the pods in the default namespace or `kubectl get pods -A` to show all pods in all namespaces

6. Now we build the container `docker build -t hello-world:1 .` (no push to docker hub or other registry)

7. Next we run the imperative command `kubectl run hello-world --image=hello-world:1`

8. We can now see the pod `kubectl get pods -o wide`. If you check `curl http://localhost:8080` you will not see the hello world message probably

9. Run `kubectl port-forward hello-world 8080:8080 &` and then `curl http://localhost:8080` and you should see the hello world message then you can will the forwarding.

10. Now we will delete the pod `kubectl delete pod hello-world` then lets do it nicely

11. Run `kubectl run hello-world --image=hello-world:1 --port=8080 && sleep 5 && kubectl port-forward pod/hello-world 8080:8080 &` and then `curl http://localhost:8080` and you should see the hello world message.

11. Lets now see the pod with `kubectl get pods -o wide` and more details with `kubectl describe pod hello-world`

12. Lets now stop the port forwarding with `kill -9 $(ps aux | grep 'kubectl port-forward pod/hello-world 8080:8080' | grep -v grep | awk '{print $2}')` then `kubectl delete pod hello-world`

> Running commands in the background and using sleep might not always be reliable, especially if the pod takes longer to get ready. Monitoring the pod's status programmatically would be more robust.
>The method to find and kill the port-forwarding process is dependent on the environment and how uniquely identifiable the process is. The grep command should be as specific as possible to avoid false matches.

13. Now imperative object configuration lets you create objects by specifying the action to take (e.g., create, update, delete) while using a configuration file. A configuration file, hello-world-create.yaml, is provided to you in this directory

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-world
spec:
  containers:
  - name: hello-world
    image: hello-world:1
    ports:
    - containerPort: 8080
```

14. Lets now run `kubectl create -f hello-world-create.yaml` and then `kubectl get pods -o wide` and `kubectl describe pod hello-world`. But the pod will not work due to missing forwarding. The YAML manifest provided defines a Kubernetes Pod with a container running your hello-world:1 image and exposes port 8080 within the container. However, in Kubernetes, port forwarding to your local machine isn't something that can be defined directly in the Pod manifest. Finally `kubectl delete pod hello-world`


### Time to move to declarative configuration

Here is the declarative (local) configuration file

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  generation: 1
  labels:
    run: hello-world
  name: hello-world
spec:
  replicas: 3
  selector:
    matchLabels:
      run: hello-world
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
    type: RollingUpdate
  template:
    metadata:
      labels:
        run: hello-world
    spec:
      containers:
      - image: hello-world:1
        name: hello-world
        ports:
        - containerPort: 8080
          protocol: TCP
        resources:
          limits:
            cpu: 2m
            memory: 30Mi
          requests:
            cpu: 1m
            memory: 10Mi   
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      securityContext: {}
      terminationGracePeriodSeconds: 30
```

1. Run `kubectl apply -f hello-world-apply.yaml` or `kubectl apply -f local-apply.yaml`

2. Inspect the pods with `kubectl get pods -o wide` and `kubectl get deployments -o wide`

3. Lets try the kube capacity to self-heal: `kubectl delete pod hello-world-<pod-id>` and `kubectl get pods -o wide` 

4. Now lets expose and test the load balancing features of Kubernetes. You can run `kubectl expose deployment hello-world --type=NodePort --port=8080` but first lets try a different way and run `kubectl expose deployment/hello-world` then in another terminal run `kubectl proxy`

5. First try the service with `curl -L http://localhost:8001/api/v1/namespaces/default/services/hello-world/proxy/` then run
```bash
for i in `seq 10`; do curl -L http://localhost:8001/api/v1/namespaces/default/services/hello-world/proxy/; done
```
and observe how different pods are used.
```
Hello world from hello-world-85dfd74cc-trcgx! Your app is up and running!
Hello world from hello-world-85dfd74cc-jtr7c! Your app is up and running!
Hello world from hello-world-85dfd74cc-8qtbn! Your app is up and running!
Hello world from hello-world-85dfd74cc-8qtbn! Your app is up and running!
Hello world from hello-world-85dfd74cc-jtr7c! Your app is up and running!
Hello world from hello-world-85dfd74cc-jtr7c! Your app is up and running!
Hello world from hello-world-85dfd74cc-8qtbn! Your app is up and running!
Hello world from hello-world-85dfd74cc-trcgx! Your app is up and running!
Hello world from hello-world-85dfd74cc-jtr7c! Your app is up and running!
Hello world from hello-world-85dfd74cc-trcgx! Your app is up and running!
```

6. Cleanup time: `kubectl delete deployment/hello-world service/hello-world` and `CTRL+C` to stop the proxy

7. Now lets modify the `yaml` file in order to have the exposing & access included:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-world
spec:
  replicas: 3
  selector:
    matchLabels:
      run: hello-world
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
    type: RollingUpdate
  template:
    metadata:
      labels:
        run: hello-world
    spec:
      containers:
      - image: hello-world:1
        name: hello-world
        ports:
        - containerPort: 8080
          protocol: TCP
        resources:
          limits:
            cpu: 2m
            memory: 30Mi
          requests:
            cpu: 1m
            memory: 10Mi
---
apiVersion: v1
kind: Service
metadata:
  name: hello-world-service
spec:
  type: NodePort
  selector:
    run: hello-world
  ports:
    - protocol: TCP
      port: 8080
      nodePort: 30080  # Optional: Remove or change this if you want Kubernetes to assign a port automatically
```

8. Now re-test the balacing with `for i in `seq 10`; do curl -L http://localhost:30080; done`

9. When you run the cleanup now with `kubectl delete deployment/hello-world` you will see that at `kubectl get pods -o wide` you will get something in line with:
```
NAME                          READY   STATUS        RESTARTS   AGE     IP          NODE             NOMINATED NODE   READINESS GATES
hello-world-85dfd74cc-9f58d   1/1     Terminating   0          9m21s   10.1.0.23   docker-desktop   <none>           <none>
hello-world-85dfd74cc-bqfng   1/1     Terminating   0          9m21s   10.1.0.22   docker-desktop   <none>           <none>
hello-world-85dfd74cc-c5k5n   1/1     Terminating   0          9m21s   10.1.0.24   docker-desktop   <none>           <none>
```
Meaning the pods are in process of being terminated. If you run `kubectl get pods -o wide` again after a while you will see that the pods are gone. Also cleanup the service with `kubectl service/hello-world` and `CTRL+C` to stop the proxy if any

