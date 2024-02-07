# Setup NFS for Neural cluster

The purpose of this document is to setup NFS storage on a bare-metal Kubernetes cluster and use it to store data for various applications.

## Asumptions

 - Master node 1: 192.168.1.55
 - Worker node 1: 192.168.1.51
 - Worker node 2: 192.168.1.52
 - Worker node 3: 192.168.1.53
 - Worker node 4: 192.168.1.54
 - NFS Server:    192.168.1.56

## Install

To set up NFS storage on a bare-metal Kubernetes cluster and then use it, you will need to follow these general steps:

### Step 1: Set Up an NFS Server

1. **Install NFS on a Server**:
    - On an Ubuntu server, you can install NFS by running:
      ```
      sudo apt update
      sudo apt install nfs-kernel-server
      ```

2. **Create and Export the NFS Share**:
    - Create a directory to share via NFS:
      ```
      sudo mkdir -p /srv/nfs/k8s
      ```
    - Assign proper permissions (modify as needed for your environment):
      ```
      sudo chown nobody:nogroup /srv/nfs/k8s
      sudo chmod 777 /srv/nfs/k8s
      ```
    - Edit the `/etc/exports` file to make the share available to your Kubernetes nodes:
      ```
      /srv/nfs/k8s    *(rw,sync,no_subtree_check,insecure)
      ```
    - Apply the export settings:
      ```
      sudo exportfs -rav
      ```
    - Ensure the NFS service is running:
      ```
      sudo systemctl restart nfs-kernel-server
      ```

### Step 2: Install NFS Client on Kubernetes Nodes

On each of your Kubernetes nodes (both master and worker nodes), install the NFS client package:

- On Ubuntu:
  ```
  sudo apt update
  sudo apt install nfs-common
  ```

### Step 3: Create a PersistentVolume (PV) in Kubernetes

Create a PersistentVolume manifest (`nfs-pv.yaml`) that points to your NFS server:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.1.56  # Replace with your NFS server IP or hostname
    path: "/srv/nfs/k8s"
```

Apply the manifest to your cluster:

```
kubectl apply -f nfs-pv.yaml
```

### Step 4: Create a PersistentVolumeClaim (PVC)

Create a PVC manifest (`nfs-pvc.yaml`) to claim some of the storage provided by your PV:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
```

Apply the manifest:

```
kubectl apply -f nfs-pvc.yaml
```

### Step 5: Using the NFS Volume in a Deployment

Create a deployment manifest (`nfs-deployment.yaml`) that uses the PVC:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nfs-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nfs-client
  template:
    metadata:
      labels:
        app: nfs-client
    spec:
      containers:
      - name: app
        image: nginx
        volumeMounts:
        - name: nfs-volume
          mountPath: /usr/share/nginx/html
      volumes:
      - name: nfs-volume
        persistentVolumeClaim:
          claimName: nfs-pvc
```

Apply the deployment:

```
kubectl apply -f nfs-deployment.yaml
```

This deployment will create pods that have the NFS volume mounted, allowing them to read and write to the NFS server.

### Note:

- Ensure your NFS server's firewall is configured to allow traffic from your Kubernetes nodes.
- The `accessModes: ReadWriteMany` allows the volume to be mounted by multiple nodes simultaneously, which is necessary for some applications but also depends on the capabilities of your storage system (NFS in this case supports it).

These steps outline how to manually set up and use NFS storage within a Kubernetes cluster on bare metal. Always test your setup in a development environment before moving to production.

## Simple low-level testing

To perform a simple test of writing and reading data across workers in your Kubernetes cluster using NFS (assuming you've set up NFS as per the previous instructions and your NFS volume is accessible from all workers), follow these steps:

### Step 1: Test NFS Mount on Worker Nodes

First, manually test the NFS mount on your worker nodes to ensure they can correctly mount the NFS share and read/write data.

1. **Mount the NFS Share on a Worker Node**:
- Pick a worker node and SSH into it.
- Create a mount point (e.g., `/mnt/nfs`):
```bash 
sudo mkdir -p /mnt/nfs
```
- Mount the NFS share:

```bash
sudo mount -t nfs 192.168.1.56:/srv/nfs/k8s /mnt/nfs
```

2. **Write Data**:
    - On the same worker node, write some data to a file in the NFS share:
```bash
echo "Hello from $(hostname)" | sudo tee /mnt/nfs/testfile.txt
```

3. **Unmount the NFS Share**:
    - Once done, unmount the NFS share:
```bash
sudo umount /mnt/nfs
```

### Step 2: Verify Data from Another Worker Node

Repeat the process on a different worker node to verify that you can see and read the data written by the first node.

1. **Mount the NFS Share on Another Worker Node**:
    - SSH into another worker node.
    - Create a mount point if it doesn't exist:
      ```
      sudo mkdir -p /mnt/nfs
      ```
    - Mount the NFS share:
      ```
      sudo mount -t nfs 192.168.1.56:/srv/nfs/k8s /mnt/nfs
      ```

2. **Read Data**:
    - Read the file written by the first worker:
      ```
      cat /mnt/nfs/testfile.txt
      ```
    - You should see the content written by the first worker node, confirming that the NFS setup is working across nodes.

3. **Unmount the NFS Share**:
    - Unmount the NFS share before leaving:
      ```
      sudo umount /mnt/nfs
      ```

### Step 3: Clean Up

- Remember to clean up after your tests by removing the test files from the NFS share and unmounting the NFS shares on both worker nodes.

This manual test ensures that your NFS setup is correctly configured for cross-worker communication and data persistence, providing a simple way to verify the NFS storage before using it in Kubernetes workloads.


## Testing

To test NFS storage in Kubernetes and demonstrate that data written by one pod on one node is available to another pod on another node, you can follow a simple approach using two pods and a shared NFS volume. Here's how:

### Step 1: Ensure NFS is Setup and Accessible

Before starting, ensure your NFS server is set up correctly and accessible from all Kubernetes nodes, as discussed in previous steps.

### Step 2: Create a PersistentVolume (PV) and PersistentVolumeClaim (PVC)

First, define a PersistentVolume that points to your NFS share and a PersistentVolumeClaim for pods to use.

**PersistentVolume (pv.yaml):**

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: nfs-server.example.com  # Replace with your NFS server address
    path: "/srv/nfs/k8s"
```

**PersistentVolumeClaim (pvc.yaml):**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Gi
```

Apply these configurations:

```shell
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
```

### Step 3: Deploy Test Pods

Deploy two pods in different nodes (if possible, to ensure cross-node communication) that use the PVC.

**Pod 1 (write-test.yaml):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: write-test
spec:
  containers:
  - name: writer
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "echo Hello from write-test > /data/testfile.txt && sleep 3600"]
    volumeMounts:
    - name: nfs
      mountPath: "/data"
  volumes:
  - name: nfs
    persistentVolumeClaim:
      claimName: nfs-pvc
```

**Pod 2 (read-test.yaml):**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: read-test
spec:
  containers:
  - name: reader
    image: busybox
    command: ["/bin/sh"]
    args: ["-c", "sleep 30 && cat /data/testfile.txt && sleep 3600"]
    volumeMounts:
    - name: nfs
      mountPath: "/data"
  volumes:
  - name: nfs
    persistentVolumeClaim:
      claimName: nfs-pvc
```

Apply these configurations:

```shell
kubectl apply -f write-test.yaml
kubectl apply -f read-test.yaml
```

### Step 4: Verify the Test

After both pods are up, check the logs of the `read-test` pod to see if it successfully reads the data written by the `write-test` pod.

```shell
kubectl logs read-test
```

You should see the message "Hello from write-test" in the logs, indicating that the `read-test` pod successfully read the data written by the `write-test` pod on the shared NFS volume, demonstrating cross-node data sharing.

### Clean-up

Remember to clean up your resources after testing:

```shell
kubectl delete pod write-test read-test
kubectl delete pvc nfs-pvc
kubectl delete pv nfs-pv
```

This simple test shows how NFS can be used to share data between pods across different nodes in a Kubernetes cluster.

### Advanced Testing

To modify the test so that the `write-test` pod writes the hostname and current time to a file every 5 seconds, and the `read-test` pod reads this file every 5 seconds, we need to adjust the command arguments for both containers. Here is a new approach of using Deployment to test this.

### Adjusted Pod Manifests

#### Deployment: Write Test (write-test.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-nfs-deployment
spec:
  replicas: 4
  selector:
    matchLabels:
      app: test-nfs-deployment
  template:
    metadata:
      labels:
        app: test-nfs-deployment
    spec:
      containers:
      - name: test-nfs-deployment
        image: busybox
        command: ["/bin/sh", "-c"]
        args: 
        - |
          while true; do
            echo "$(date): Written by $(hostname)" >> /data/testfile.txt
            sleep $((5 + RANDOM % 6))  # Sleeps for a random time between 5 and 10 seconds
          done
        volumeMounts:
        - name: nfs-volume
          mountPath: "/data"
      volumes:
      - name: nfs-volume
        persistentVolumeClaim:
          claimName: nfs-pvc

```

This pod continuously writes the current date and hostname to `/data/testfile.txt` every 5 seconds.

#### Pod 2: Read Test (read-test.yaml)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: read-test
spec:
  containers:
  - name: reader
    image: busybox
    command: ["/bin/sh", "-c"]
    args: 
    - |
      while true; do
        if [ -f /data/testfile.txt ]; then
          cat /data/testfile.txt
        else
          echo "Waiting for file..."
        fi
        sleep 5
      done
    volumeMounts:
    - name: nfs
      mountPath: "/data"
  volumes:
  - name: nfs
    persistentVolumeClaim:
      claimName: nfs-pvc
```

This pod attempts to read from `/data/testfile.txt` every 5 seconds, printing its contents if the file exists.

#### Deploying and Observing the Pods

1. **Deploy the Pods**:

    Apply the configurations:

    ```shell
    kubectl apply -f write-test.yaml
    kubectl apply -f read-test.yaml
    ```

2. **Observe the Write Operation**:

    Monitor the logs of the `write-test` pod:

    ```shell
    kubectl logs -f write-test
    ```

    You should see messages being logged every 5 seconds with the current date and the hostname of the pod.

3. **Observe the Read Operation**:

    In another terminal, monitor the logs of the `read-test` pod:

    ```shell
    kubectl logs -f read-test
    ```

    You should see the same messages as in the `write-test` pod's logs, indicating that the `read-test` pod is successfully reading the updates made by the `write-test` pod to the shared NFS volume.

This simple exercise demonstrates how NFS can be used to share data between pods in a Kubernetes environment, enabling scenarios where multiple pods need to access and manipulate shared data.
