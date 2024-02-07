# Workshop 2: Scaling, services, deployment strategies and other

Table of contents
=================
 - [ReplicaSets](#replicasets)
 - [Autoscaling](#autoscaling)
 - [Deployment strategies](#deployment-strategies)
 - [ConfigMaps and Secrets](#configmaps)
 - [Service Binding](#service-binding)
 - [Hands-on](#hands-on)  
   - [Windows metrics server installation](#windows-metrics-server-installation)
 - [Cheat sheet](#cheat-sheet)


  

## ReplicaSets

<p align="center"> <img src="img/k8s-replicasets1.png" width="700"/> </p>

A ReplicaSet is a Kubernetes object that ensures that a specified number of pod replicas are running at any given time. It is a higher-level abstraction than pods and is used to guarantee the availability of a specified number of identical pods. The replicasets are not created directly but rather through a higher-level abstraction called a deployment.

In [Workshop 1](./workshop1.md), we already tested the automatic state recovery of pods performed by the ReplicaSet. 

<p align="center"> <img src="img/k8s-replicasets2.png" width="700"/> </p>


## Autoscaling

<p align="center"> <img src="img/k8s-autoscaling1.png" width="700"/> </p>


## Deployment strategies

### Overview

A Kubernetes deployment strategy defines an application’s lifecycle that achieves and maintains the configured state for objects and applications in an automated manner. Effective deployment strategies minimize risk.

Kubernetes deployment strategies are used to: 

 - Deploy, update, or rollback ReplicaSets, Pods, Services, and Applications 

 - Pause/Resume Deployments 

 - Scale Deployments manually or automatically 

### Types of deployment strategies

The following are six types of deployment strategies:


#### Recreate
 - Recreate: Terminates the old version by simultaneously shutting down all the pods and then creates new pods with the new version.
<center><img src="img/recreate-strategy.png" width=700></center>

   - Pros: Simple and fast.
   - Cons: Downtime during the deployment.

#### Ramped
 - Rolling: Gradually terminates the old version by creating new pods with the new version and then terminating the old pods.
 <center><img src="img/rolling-ramped-strategy.png" width=700></center>

   - Pros: No downtime during the deployment.
   - Cons: Slow and you cannot control traffic between the old and new versions!

#### Blue/Green

 - Blue/green: Creates a new version of the application and then switches the traffic to the new version. In a blue/green strategy, the blue environment is the live version of the application. The green environment is an exact copy that contains the deployment of the new version of the application. The green environment is thoroughly tested. Once all changes, bugs, and issues are addressed, user traffic is switched from the blue environment to the green environment.
   - Pros: No downtime during the deployment.
   - Cons: Expensive because you need to have two identical environments.

#### Canary

 - Canary: In a canary strategy, the new version of the application is tested using a small set of random users alongside the current live version of the application. Once the new version of the application is successfully tested, it is then rolled out to all users. 
   - Pros: Multiple versions can run in parallel. Full control over traffic distribution 
   - Cons: Requires intelligent load balancer. 

#### A/B Testing

 - A/B testing: The A/B testing strategy, also known as split testing, evaluates two versions of an application (version A and version B). With A/B testing, each version has features that cater to different sets of users. You can select which version is best for global deployment based on user interaction and feedback. 
   - Pros: No downtime during the deployment.
   - Cons: Complex and you need to have a good monitoring system. Difficult to troubleshoot errors for a given session, distributed tracing becomes mandatory

#### Shadow

 - Shadow: In a shadow strategy, a “shadow version” of the application is deployed alongside the live version. User requests are sent to both versions, and both handle all requests, but the shadow version does not forward responses back to the users. This lets developers see how the shadow version performs using real-world data without interrupting user experience. 

You can use either a single deployment strategy or a combination of multiple deployment strategies.


### Deployment Strategies Summary

| Strategy    | Zero Downtime | Real Traffic Testing | Targeted Users | Cloud Cost | Rollback Duration | Negative User Impact | Complexity of Setup |
|-------------|:-------------:|:--------------------:|:--------------:|:----------:|:-----------------:|:--------------------:|:-------------------:|
| Recreate    | X             | X                    | X              | •--        | •••               | •••                  | - - -               |
| Ramped      | ✓             | X                    | X              | •--        | •••               | •--                  | •--                 |
| Blue/Green  | ✓             | X                    | X              | •••        | - - -             | ••-                  | ••-                 |
| Canary      | ✓             | ✓                    | X              | •--        | •--               | •--                  | ••-                 |
| A/B Testing | ✓             | ✓                    | ✓              | •--        | •--               | •--                  | •••                 |
| Shadow      | ✓             | ✓                    | X              | •••        | - - -             | - - -                | •••                 |

#### Conclusion

- **Consider the product type and the target audience.**
- **Shadow and Canary strategies use live user requests, as opposed to using a sample of users.**
- **The A/B testing strategy is useful if the version of the application requires minor tweaks or UI feature changes.**
- **The Blue/Green strategy is useful if your version of the application is complex or critical and needs proper monitoring with no downtime during deployment.**
- **The Canary strategy is a good choice if you want zero downtime and are comfortable exposing your version of the application to the public.**
- **A rolling strategy gradually deploys the new version of the application. There is no downtime, and it is easy to roll back.**
- **The recreate strategy is a good choice if the application is not critical and users aren’t impacted by a short downtime.**

In the realm of Kubernetes and modern cloud-native applications, the choice of deployment strategy often depends on the specific needs and context of the application. However, some strategies are more commonly used due to their balance of safety, control, and complexity. Here's a brief overview:

1. **Rolling Update (Ramped)**:
   - **Usage**: This is one of the most commonly used deployment strategies in Kubernetes. It’s the default strategy for Kubernetes Deployments.
   - **Why Popular**: It allows for zero-downtime updates by incrementally updating Pods instances with new ones. This strategy ensures that the application remains available during the deployment and is a good fit for most use cases.

2. **Canary Deployments**:
   - **Usage**: Increasingly popular, especially in environments where it's crucial to reduce the risk of deploying a new version.
   - **Why Popular**: Canary deployments allow you to roll out a change to a small subset of users before rolling it out to the entire infrastructure. It’s particularly useful for catching issues that weren't found during testing and is often integrated into more mature CI/CD pipelines.

3. **Blue/Green Deployment**:
   - **Usage**: Commonly used in critical applications where you want to test the new version in the exact same environment.
   - **Why Popular**: It reduces downtime and risk by running two identical environments, only switching over once the new version is confirmed to be stable.

4. **Recreate**:
   - **Usage**: Less common compared to Rolling and Canary, mainly due to its downtime during deployment.
   - **Why Popular**: Simplicity is its key advantage. The Recreate strategy can be suitable for development, test environments, or applications where downtime is not a critical issue.

5. **A/B Testing**:
   - **Usage**: Used in applications where the new feature impact needs to be tested with actual users. It’s more about feature validation than just application updating.
   - **Why Popular**: It allows targeted roll-outs and observing user behavior, which is valuable for feature development and UX improvements.

6. **Shadow**:
   - **Usage**: Less common and used mainly in complex applications where new versions of services are tested with real data.
   - **Why Popular**: It allows full-scale testing of new releases under real-world conditions without impacting users.


- **Most Common**: Rolling updates are the most commonly used due to their balance of risk, control, and simplicity, suitable for a wide range of applications.
- **Trend**: Canary deployments are becoming more popular as they offer a safer way to release and are well-suited for continuous delivery models.
- **Complexity vs. Safety**: More complex strategies like Blue/Green, A/B Testing, and Shadow are used in specific cases where the business requirements justify the additional complexity and overhead.

Each strategy has its place, and the best choice depends on the specific requirements and constraints of the application, the organization's maturity in CI/CD practices, and the criticality of ensuring seamless user experience during updates.



## ConfigMaps

The ConfigMaps is a Kubernetes object that allows you to decouple configuration artifacts from image content to keep containerized applications portable. ConfigMaps can be used to store fine-grained information like individual properties or coarse-grained information like entire configuration files or JSON blobs.
ConfigMaps are often used to store configuration settings that are likely to change during the application lifecycle. For example, you can use ConfigMaps to store database connection strings, feature flags, environment variables, and command-line arguments.
Similarly to ConfigMaps are Secrets, which are used to store sensitive information like passwords, OAuth tokens, and SSH keys. Secrets are similar to ConfigMaps, but they are base64 encoded and only mounted to the container filesystem when needed.


## Service binding

Service binding in Kubernetes refers to the process of connecting applications deployed on Kubernetes to external resources and services, such as databases, message queues, or other services, <u>**whether they are inside or outside the Kubernetes cluster**</u>. This concept is particularly important in cloud-native environments where applications often depend on various external services for their operations.

<center> <img src="img/service-binding.png" width="700"></center>

### Key Aspects of Service Binding in Kubernetes:

1. **Connection Details**: Service binding typically involves providing the necessary connection details (such as URLs, credentials, certificates, etc.) from the external service to the Kubernetes application. This information is essential for the application to interact with the service.

2. **Secrets Management**: Sensitive information like passwords or tokens are often managed using Kubernetes Secrets. These secrets can be mounted into application pods or made available as environment variables.

3. **ConfigMaps**: For non-sensitive configuration data, Kubernetes ConfigMaps are often used. They can store connection details like URLs or configuration parameters, which can be injected into the application.

4. **Service Binding Operators**: In more complex scenarios or in cloud-native environments, operators can be used to automate the service binding process. These operators can handle the detection of available services and the automatic injection of connection details into applications.

5. **Portability and Flexibility**: Service binding enables applications to be more portable and flexible, as they can be easily connected to different services without changing the application's core logic.

6. **Service Brokers**: In cloud environments, service brokers can be used to provision and bind services to applications. The Cloud Foundry Service Broker API is one such example that has been adopted by various cloud providers.

7. **Service Meshes**: In advanced scenarios, especially in microservices architectures, service meshes like Istio can manage service-to-service communications, providing an additional layer for handling service discovery and connectivity.

### Example Scenario:

- An application running in a Kubernetes cluster requires access to a PostgreSQL database.
- A Secret in Kubernetes is created with the database credentials.
- The deployment configuration for the application includes a reference to this Secret, injecting the credentials as environment variables into the application pods.
- The application uses these environment variables to establish a connection to the PostgreSQL database.

### Conclusion:

Service binding is a critical aspect of cloud-native application development and deployment, ensuring that applications can securely and efficiently connect to the services they depend on. This process is key to creating dynamic, scalable, and maintainable applications in Kubernetes environments.


## Hands-on

In this lab, you will:

  - Scale an application with a ReplicaSet
  - Apply rolling updates to an application
  - Use a ConfigMap to store application configuration
  - Autoscale the application using Horizontal Pod Autoscaler


1. Build hello-world image with `docker build -t heelo-world:1 .`

2. Apply the deployment with `kubectl apply -f local.yaml` then expose the service with `kubectl expose deployment/hello-world`

3. Run in another terminal `kubectl proxy` to access the app

4. Test the deployment with `curl -L http://localhost:8001/api/v1/namespaces/default/services/hello-world/proxy/`
```
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
```

5. Now lets scale up the deployment with `kubectl scale deployment/hello-world --replicas=5` and test again with multiple queries `for i in `seq 10`; do curl -L localhost:8001/api/v1/namespaces/default/services/hello-world/proxy; done`
```
Hello world from hello-world-85dfd74cc-h5qrj! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-h5qrj! Your app is up and running!
Hello world from hello-world-85dfd74cc-s4h24! Your app is up and running!
Hello world from hello-world-85dfd74cc-s4h24! Your app is up and running!
Hello world from hello-world-85dfd74cc-ckkl8! Your app is up and running!
Hello world from hello-world-85dfd74cc-hxdwb! Your app is up and running!
Hello world from hello-world-85dfd74cc-hxdwb! Your app is up and running!
Hello world from hello-world-85dfd74cc-ckkl8! Your app is up and running!
Hello world from hello-world-85dfd74cc-ckkl8! Your app is up and running!
```


6. Then scale down and test with `kubectl scale deployment/hello-world --replicas=1` and `for i in `seq 10`; do curl -L localhost:8001/api/v1/namespaces/default/services/hello-world/proxy; done`

```
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
Hello world from hello-world-85dfd74cc-4msb9! Your app is up and running!
```

7. Now lets try a rollout. Modify the code and build with `docker build -t hello-world:2 .` changing the tag

8. Now if we check the deployment with `kubectl get deployments -o wide` we can see that the image is not updated yet so we run:
```bash
kubectl set image deployment/hello-world hello-world=hello-world:2
```

Then we  check again `kubectl get deployments -o wide` to obtain something similar to:
```
NAME          READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS    IMAGES          SELECTOR
hello-world   1/1     1            1           16m   hello-world   hello-world:2   run=hello-world
```

9. Running now the curl with `curl -L localhost:8001/api/v1/namespaces/default/services/hello-world/proxy` we can see the new version
```
Welcome to (v2) hello-world-d974685bb-zc74s! Your app is up and running!
```

10. Now lets rollback with `kubectl rollout undo deployment/hello-world` and check again `curl -L localhost:8001/api/v1/namespaces/default/services/hello-world/proxy`. First we get
```
{
  "kind": "Status",
  "apiVersion": "v1",
  "metadata": {},
  "status": "Failure",
  "message": "error trying to reach service: dial tcp 10.1.0.35:8080: connect: connection refused",
  "reason": "ServiceUnavailable",
  "code": 503
}
```
and then we can run `kubectl rollout status deployment/hello-world` to check the status of the deployment followed by another curl to see the old version
```
Hello world from hello-world-85dfd74cc-j67zm! Your app is up and running!
```

11. Checking the image with `kubectl get deployments -o wide` we can see that the image is now the old one
```
NAME          READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS    IMAGES          SELECTOR
hello-world   1/1     1            1           22m   hello-world   hello-world:2   run=hello-world
```

11. Now lets cleanup the deployment with `kubectl delete deployment/hello-world service/hello-world` and `CTRL+C` to stop the proxy. The `delete` command will cleanup both the deployment and the service.

## ConfigMaps

ConfigMaps and Secrets are used to store configuration information separate from the code so that nothing is hardcoded. It also lets the application pick up configuration changes without needing to be redeployed. To demonstrate this, we’ll store the application’s message in a ConfigMap so that the message can be updated simply by updating the ConfigMap.

> Fot this second part of the lab you can leave the proxy on as well as the service from previous part.

1. Create a ConfigMap with `kubectl create configmap test-app-config --from-literal=TEST_MESSAGE="Hello world from ConfigMap!"`

2. Check the ConfigMap with `kubectl describe configmap/test-app-config` and `kubectl get configmaps test-app-config -o yaml`. 


3. Build `docker build -t hello-world:3 -f Dockerfile_configmap .` then apply the deployment with `kubectl apply -f local-configmap-env-ver.yaml` and expose the service with `kubectl expose deployment/hello-world` and start `kubectl proxy` to test the app with `curl -L localhost:8001/api/v1/namespaces/default/services/hello-world/proxy` you should see:
```
Hello world from ConfigMap!
```

5. Next we modify the message within configmap with:
```bash
kubectl delete configmap test-app-config && kubectl create configmap test-app-config --from-literal=TEST_MESSAGE="This message is different, and you didn't have to rebuild the image!"
```

6. Now we need to restart so that the env vars are reloaded. We can do this with 
```bash
kubectl rollout restart deployment/hello-world
```

7. Run the `curl -L localhost:8001/api/v1/namespaces/default/services/hello-world/proxy` again and you should see the new message:
```
This message is different, and you didn't have to rebuild the image!
```

8. Check the rollout history
```bash
kubectl rollout history deployment/hello-world
``` 


## Autoscaling

1. Start the deployment with
```bash
kubectl apply -f local-hpa.yaml
```

2. Now we need to create a Horizontal Pod Autoscaler (HPA) with 
```bash
kubectl autoscale deployment hello-world-hpa --cpu-percent=5 --min=1 --max=10
```
and 

3. Now open a new terminal and spam the service :) with:
```bash
for i in `seq 100000`; do curl -L localhost:8001/api/v1/namespaces/default/services/hello-world-hpa/proxy; done
```

> NOTE: you need to make sure the metrics server is running - try a `kubectl top nodes` to check. See below Windows installation notes.

4. After everything you should close the proxy and cleanup with:
```bash
kubectl delete deployment/hello-world-hpa service/hello-world-hpa hpa/hello-world-hpa
```


### Windows metrics server installation

To install Metrics Server on Docker Desktop for Windows, which does not include Metrics Server in its default Kubernetes installation, you can follow these steps:

1. **Download the `components.yaml` File**:
   - Download the latest `components.yaml` file from the [Metrics Server releases page on GitHub](https://github.com/kubernetes-sigs/metrics-server/releases).

2. **Modify the `components.yaml`**:
   - Before applying the file, you need to modify it. Open `components.yaml` in a text editor and add the line `--kubelet-insecure-tls` under the `args` section【115†source】. This is necessary to avoid TLS-related errors when Metrics Server attempts to communicate with kubelets.

3. **Apply the Configuration**:
   - Apply the changes with the following command:
     ```bash
     kubectl apply -f components.yaml
     ```
   - This command will deploy Metrics Server to your Kubernetes cluster【116†source】.

4. **Wait for it...**
   - Wait for a few seconds to allow the metrics services to statup. You can check the status of the deployment with the following command:
     ```bash
     kubectl get deployment metrics-server -n kube-system
     ```

5. **Verify the Installation**:
   - After applying the configuration, verify that Metrics Server is working correctly by running:
     ```bash
     kubectl top node
     kubectl top pod -A
     ```
   - These commands should now return metrics for your nodes and pods, indicating that Metrics Server is operational【117†source】.

By following these steps, you should be able to set up Metrics Server in your Docker Desktop Kubernetes environment on Windows, enabling features like Horizontal Pod Autoscaler (HPA) to function correctly.


## Cheat sheet

| Command                         | Description                                      |
|---------------------------------|--------------------------------------------------|
| `kubectl autoscale deployment`  | Autoscales a Kubernetes Deployment.              |
| `kubectl create configmap`      | Creates a ConfigMap resource.                    |
| `kubectl get deployments -o wide`| Lists deployments with details.                 |
| `kubectl get hpa`               | Lists Horizontal Pod Autoscalers (hpa).         |
| `kubectl scale deployment`      | Scales a deployment.                             |
| `kubectl set image deployment`  | Updates the current deployment.                  |
| `kubectl rollout`               | Manages the rollout of a resource.               |
| `kubectl rollout restart`       | Restarts the resource so that the containers restart. |
| `kubectl rollout undo`          | Rollbacks the resource.                          |

