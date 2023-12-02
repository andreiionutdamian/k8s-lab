# Workshop 2 IBM K8s course on Coursera


## Introduction to Kubernetes

<p align="center"> <img src="img/k8s-control-plane.png" alt="K8s Control Plane" width="700"/></p>
The control plane works on the "master" node. It is responsible for managing the cluster. It is made up of the following components:
- kube-apiserver: responsible for exposing the Kubernetes API
- etcd: responsible for storing the cluster state
- kube-scheduler: responsible for scheduling the pods
- kube-controller-manager: responsible for controlling the cluster
- cloud-controller-manager: responsible for interacting with the underlying cloud provider

A control plane can have one or more master nodes. The master nodes are managed by a cluster manager. The cluster manager is responsible for managing the lifecycle of the master nodes. It is also responsible for managing the lifecycle of the worker nodes.

The worker nodes are responsible for running the pods. A pod is a group of one or more containers. The worker nodes are managed by a node agent. The node agent is responsible for managing the lifecycle of the worker nodes. It is also responsible for managing the lifecycle of the pods.

The communication between the control plane and the worker plane is done through the Kubernetes API. The communication between the worker nodes is done through the Kubernetes API.


<p align="center"><img src="img/k8s-worker-plane.png" alt="K8s Worker Plane" width="700"/></p>
The worker plane works on the "worker" node. It is responsible for running the pods. It is made up of the following components:

 - kubelet: responsible for running the pods
 - kube-proxy: responsible for routing the traffic to the pods
 - container runtime: responsible for running the containers

Kubernetes objects can be created and managed either imperatively or declaratively, though some objects are more commonly associated with one approach than the other. Below is a summary of key Kubernetes objects, categorized based on the approach typically used to manage them:

### Commonly Managed Imperatively

1. **Pods**:
   - Basic unit of deployment in Kubernetes.
   - Contains one or more containers.
   - Often created imperatively for debugging or quick tests (e.g., `kubectl run`).

2. **Services**:
   - Defines a logical set of Pods and a policy to access them.
   - Types include ClusterIP, NodePort, and LoadBalancer.
   - Can be created imperatively, especially for quick exposure of Pods (e.g., `kubectl expose`).

3. **ConfigMaps and Secrets**:
   - ConfigMaps: Used to store non-confidential data in key-value pairs.
   - Secrets: Used to store sensitive information.
   - Often created imperatively for simplicity (e.g., `kubectl create configmap`, `kubectl create secret`).

### Commonly Managed Declaratively

1. **Deployments**:
   - Provides declarative updates for Pods and ReplicaSets.
   - Ideal for stateless application management.
   - Commonly used with YAML files and `kubectl apply`.

2. **StatefulSets**:
   - Manages stateful applications.
   - Provides stable, unique network identifiers, stable persistent storage, and ordered, graceful deployment and scaling.
   - Typically managed declaratively.

3. **DaemonSets**:
   - Ensures that all (or some) Nodes run a copy of a Pod.
   - Common use cases are running a cluster storage daemon on every node, running a logs collection daemon on every node, etc.
   - Usually created and managed declaratively.

4. **Ingress**:
   - Manages external access to the services in a cluster, typically HTTP.
   - Provides load balancing, SSL termination, and name-based virtual hosting.
   - Declaratively defined using Ingress resources.

5. **PersistentVolumes and PersistentVolumeClaims**:
   - PersistentVolumes (PVs): Represents storage provisioned by an administrator.
   - PersistentVolumeClaims (PVCs): A request for storage by a user.
   - Typically managed declaratively to ensure consistent and reliable storage management.

6. **Jobs and CronJobs**:
   - Jobs: Creates one or more Pods and ensures that a specified number of them successfully terminate.
   - CronJobs: Manages time-based Jobs, e.g., scheduling a job execution at a certain time or interval.
   - Generally managed declaratively, especially in production use-cases.

### Conclusion

While this categorization is based on common practices, it's important to note that almost all Kubernetes objects can be managed either imperatively or declaratively. The choice often depends on the specific use case, operational practices, and scale of the environment. Declarative management is generally preferred for production environments due to its scalability, version control capabilities, and alignment with infrastructure-as-code practices.


In summary:

 - Container orchestration automates the container lifecycle resulting in faster deployments, reduced errors, higher availability, and more robust security. 

 - Kubernetes Is a highly portable, horizontally scalable, open-source container orchestration system with automated deployment and simplified management capabilities.  

 - Kubernetes architecture consists of a control plane and one or more worker planes. 

 - A control plane includes controllers, an API server, a scheduler, and an etcd. 

 - A worker plane includes nodes, a kubelet, container runtime, and kube-proxy. 

 - Kubernetes objects include Namespaces, Pods, ReplicaSets, Deployments, and Services. 

 - Namespaces help in isolating groups of resources within a single cluster. 

 - Pods represent a process or an instance of an app running in the cluster. 

 - ReplicaSets create and manage horizontally scaled running Pods. 

 - Deployments provide updates for Pods and ReplicaSets. 

 - A service in Kubernetes is a REST object that provides policies for accessing the pods and cluster. 

 - Kubernetes capabilities include automated rollouts and rollbacks, storage orchestration, horizontal scaling, automated bin packing, secret and configuration management, Ipv4/Ipv6 dual-stack support, batch execution, self-healing, service discovery, load balancing, and extensible design. 

 - Services in Kubernetes are REST objects that provide policies for accessing the pods and cluster. ClusterIP provides Inter-service communication within the cluster; a NodePort Service creates and routes the incoming requests automatically to the ClusterIP Service; the External Load Balancer, or ELB, creates NodePort and ClusterIP Services automatically and External Name service represents external storage as well as enables Pods from different namespaces to talk to each other.

 - Ingress is an API object that provides routing rules to manage external users' access to multiple services in a Kubernetes cluster; whereas using a DaemonSet ensures that there is at least one copy of the pod on all nodes; a StatefulSet manages stateful applications, manages Pod deployment and scaling, maintains a sticky identity for each Pod request and provides persistent storage volumes for your workloads and lastly a Job creates pods and tracks the Pod completion process; Jobs are retried until completed.  


Cheat Sheet: Understanding Kubernetes Architecture


| Command                     | Description                                                       |
|-----------------------------|-------------------------------------------------------------------|
| `for …do`                   | Runs a for command multiple times as specified.                   |
| `kubectl apply`             | Applies a configuration to a resource.                            |
| `kubectl config get-clusters`| Displays clusters defined in the kubeconfig.                      |
| `kubectl config get-contexts`| Displays the current context.                                     |
| `kubectl create`            | Creates a resource.                                               |
| `kubectl delete`            | Deletes resources.                                                |
| `kubectl describe`          | Shows details of a resource or group of resources.                |
| `kubectl expose`            | Exposes a resource to the internet as a Kubernetes service.       |
| `kubectl get`               | Displays resources.                                               |
| `kubectl get pods`          | Lists all the Pods.                                               |
| `kubectl get pods -o wide`  | Lists all the Pods with details.                                  |
| `kubectl get deployments`   | Lists the deployments created.                                    |
| `kubectl get services`      | Lists the services created.                                       |
| `kubectl proxy`             | Creates a proxy server between a localhost and the Kubernetes API server. |
| `kubectl run`               | Creates and runs a particular image in a pod.                     |
| `kubectl version`           | Prints the client and server version information.                  |

This table provides a quick reference to some common Kubernetes commands and their descriptions.