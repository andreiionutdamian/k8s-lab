# GlusterFS server side

> Note: Replace server names with your own.

```bash
sudo gluster peer probe PreProd-K8s-GlusterFs01
sudo gluster peer probe PreProd-K8s-GlusterFs02
sudo gluster peer probe PreProd-K8s-GlusterFs03
sudo gluster volume create pre-storage disperse 3 redundancy 1 PreProd-K8s-GlusterFs01:/GlusterFs/Brick01/Vol01 PreProd-K8s-GlusterFs02:/GlusterFs/Brick01/Vol01 PreProd-K8s-GlusterFs03:/GlusterFs/Brick01/Vol01
```

Install GlusterFS client

```bash
sudo apt update -y
sudo apt install glusterfs-client -y
glusterfs --version
```

Now lets test a volume of our (already working) GlusterFS cluster.

```bash
sudo mkdir -p /mnt/glusterfs
sudo mount -t glusterfs server1:/ProdK8sVol01 /mnt/glusterfs
```

