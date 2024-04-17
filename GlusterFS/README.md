# GlusterFS Notes

## GlusterFS server side

> Note: Replace server names with your own.

```bash
sudo gluster peer probe PreProd-K8s-GlusterFs01
sudo gluster peer probe PreProd-K8s-GlusterFs02
sudo gluster peer probe PreProd-K8s-GlusterFs03
sudo gluster volume create pre-storage disperse 3 redundancy 1 PreProd-K8s-GlusterFs01:/GlusterFs/Brick01/Vol01 PreProd-K8s-GlusterFs02:/GlusterFs/Brick01/Vol01 PreProd-K8s-GlusterFs03:/GlusterFs/Brick01/Vol01
```

## Client side 

Install GlusterFS client in worker nodes (and maybe also in the preferred master)

```bash
sudo apt update -y
sudo apt install glusterfs-client -y
glusterfs --version
```

Now lets test a volume of our (already working) GlusterFS cluster.

```bash
sudo mkdir -p /mnt/glusterfs
sudo mount -t glusterfs Prod-K8s-GlusterFs01:/ProdK8sVol01 /mnt/glusterfs
```

## Kubernetes side

Create the endpoints and the service for the GlusterFS cluster `glusterfs-endpoints.yaml`

```yaml
apiVersion: v1
kind: Endpoints
metadata:
  name: glusterfs-cluster
  labels:
    storage.k8s.io/name: glusterfs
    storage.k8s.io/part-of: kubernetes-complete-reference
    storage.k8s.io/created-by: aidamian
subsets:
  - addresses:
    - ip: 172.31.3.105
      hostname: PreProd-K8s-GlusterFs01
    - ip: 172.31.3.106
      hostname: PreProd-K8s-GlusterFs02
    - ip: 172.31.3.107
      hostname: PreProd-K8s-GlusterFs03
    ports:
    - port: 1
```

and apply the config
  
```bash
kubectl apply -f glusterfs-endpoints.yaml
```


# Finally use your endpoints in your Persistent Volume

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: glusterfs-pv
  labels:
    storage.k8s.io/name: glusterfs
    storage.k8s.io/part-of: kubernetes-complete-reference
    storage.k8s.io/created-by: aidamian
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteMany
  glusterfs:
    endpoints: glusterfs-cluster
    path: ProdK8sVol01
    readOnly: false
  persistentVolumeReclaimPolicy: Retain
```

Now ensure you have in the GlusterFS target volume a `test-app` subfolder before running the 

