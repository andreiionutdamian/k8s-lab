# 1. Download and prepare the kubespray playbooks
## Clone kubespray repo
```bash
$ git clone https://github.com/kubernetes-sigs/kubespray
```
## Move to kubespray directory
```bash
$ cd kubespray
```
## Make sure version is 2.24.0
```bash
$ git checkout v2.24.0
```

## Run fixrole.sh
Fix the ingress-controller setup.make sure you have previously copied the file to kubespray directory and it has appropriate execution rights

```bash
$ ./fixrole.sh
```


# 2. Prepare the kubespray runtime environement
## Pull pre-built kubespray runtime docker image
```bash
$ docker pull quay.io/kubespray/kubespray:v2.24.0
```

## Launch runtime
Run it in daemon mode in order to make sure that the container will run even if ssh connection to the cluster deployment controller is lost. Replace **key.pem** with appropriate filename containing the ssh key used to connect to cluster's target nodes 
```bash
$ sudo docker run -d --rm -it \
     --mount type=bind,source="$(pwd)"/inventory,dst=/kubespray/inventory \
     --mount type=bind,source="${HOME}"/.ssh/<key.pem>,dst=/root/.ssh/<key.pem> \
     --name kubespray  \
     quay.io/kubespray/kubespray:v2.24.0 bash
```
## Attach to kubespray runtime container
```bash
$ sudo docker attach kubespray
```

# 3. Setup & config files
## Make a copy of sample config directory to a new target config **newcluster**
```bash
$ cp -rfp inventory/sample inventory/**newcluster**
```

## Create the inventory file of the cluster. Make sure you replace the appropiate **IPs** of the target nodes for the cluster
```bash
$ declare -a IPS=(<IP1> <IP2> <IP2> ...<IPX>)
$ CONFIG_FILE=inventory/<newycluster>/hosts.yml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
```

The previous command will name the nodes linearly as **node1**, **node2**, and **nodeX** depending on the number of nodes. For a one 
controller node setup, edit the created file inventory/**newcluster**/hosts.yml file, change the name of the first node to 
**controller_name**, rename the other nodes with **node_nameXX**, and only use controller in the kube_control_plane groupedit the generated hosts.yml. 
```
                all:
                  hosts:
                    <controller_name>:
                       ansible_host: <IP1>
                       ansible_port: <only if the ssh port is not the default, otherwise it can be omitted>
                       ip: <IP1>
                       access_ip: <IP1>
                    <node_name01>:
                       ansible_host: <IP2>
                       ip: <IP2>
                       access_ip: <IP2>
                    ......
                    <node_nameXX>:
                       ansible_host: <IPx>
                       ip: <IPx>
                       access_ip: <IPx>
                children:
                    kube_control_plane:
                      hosts:
                        <controller_name>:
                    kube_node:
                      hosts:
                        <controller_name>:
                        <node_name01>:
                        <node_name02>:
                        .......
                        <node_nameXX>:
                    etcd:
                      hosts:
                        <controller_name>:
                        <node_name01>:
                        <node_name02>:
                    k8s_cluster:
                      children:
                        kube_control_plane:
                        kube_node:
                    calico_rr:
                      hosts: {}
```
> [!NOTE]
> You can adjust the cluster topology to best fit the target environment

## Edit the inventory/**newcluster**/group_vars/k8s_cluster/addons.yml
Make sure the following variables are set
 ```
              # dashboard
              dashboard_enabled: true

              # helm
              helm_enabled: true

              # metrics
              metrics_server_enabled: true

              # ingress
              ingress_nginx_enabled: true
              ingress_nginx_host_network: true

              # load balancer  - Make sure you have a pool of IP addresses (<IP_START>-<IP_END>) that you can allocate in "ip_range"
              metallb_enabled: true
              metallb_speaker_enabled: "{{ metallb_enabled }}"
              metallb_protocol: "layer2"
              metallb_config:
                address_pools:
                  primary:
                    ip_range:
                      - <IP_START>-<IP_END>
                    auto_assign: true
                layer2:
                  - primary
```
> [!WARNING]
> If metallb is enabled edit the *inventory/**newcluster**/group_vars/k8s_cluster/k8s-cluster.yml* file and set ***kube_proxy_strict_arp: true***

# 4. Run kubespray setup
```bash
$ ansible-playbook \
   -i inventory/<newcluster>/hosts.yml  \
   --private-key=~/.ssh/<key.pem>  \
   -u <target_user> \
   --become \
   cluster.yml
```
> [!NOTE]
> Make sure you replace **newcluster**, **key.pme** and **target_user** with appropriate values


# 5. Config nvidia runtime for GPU enabled nodes
> [!NOTE]
> Make sure the drivers are installed on the target nodes

## Install nvidia container toolkit
```bash
$ distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
$ curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
$ curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/libnvidia-container.list

$ sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
```
## Configure containerd
When running kubernetes with containerd, edit the config file which is usually present at /etc/containerd/config.toml to set up nvidia-container-runtime as the default low-level runtime:
```
version = 2
[plugins]
  [plugins."io.containerd.grpc.v1.cri"]
    [plugins."io.containerd.grpc.v1.cri".containerd]
      default_runtime_name = "nvidia"

      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia]
          privileged_without_host_devices = false
          runtime_engine = ""
          runtime_root = ""
          runtime_type = "io.containerd.runc.v2"
          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.nvidia.options]
            systemdCgroup = true
            BinaryName = "/usr/bin/nvidia-container-runtime"

```
Restart containerd
```bash
$ sudo systemctl restart containerd
```

## Enabling GPU Support in Kubernetes
Once you have configured the options above on all the GPU nodes in your cluster, you can enable GPU support by deploying the following Daemonset:

```bash
$ kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.4/nvidia-device-plugin.yml
```




