# Installation

## Initial steps

1. Install git 

```bash
sudo apt update && sudo apt install git -y
```

2. Install pip
```bash
sudo apt install python3-pip -y
```

3. Clone kubespray repo
```bash
$ git clone https://github.com/kubernetes-sigs/kubespray
```

4. Change to `kubespray` and install requirements (with or without `sudo`)

```bash
cd kubespray
pip3 install -r requirements.txt
```

5. Modify/fix a known issue

```bash
sed -i 's/\["ingress-controller-leader-{{ ingress_nginx_class }}"\]/\["ingress-controller-leader-{{ ingress_nginx_class }}","ingress-controller-leader"\]/g' roles/kubernetes-apps/ingress_controller/ingress_nginx/templates/role-ingress-nginx.yml.j2
```


## Prepare the kubespray playbooks

1. Create the new inventory `<MY_CLUSTER>`

```bash
$ cp -rfp inventory/sample inventory/<MY_CLUSTER>
```

2. Create the list of target IPs and run the initialization script
```bash
$ declare -a IPS=(<IP1> <IP2> <IP2> ...<IPX>)
$ CONFIG_FILE=inventory/<MY_CLUSTER>/hosts.yml python3 contrib/inventory_builder/inventory.py ${IPS[@]}
```

3. Edit the generated `hosts.yml` file to match the desired configuration ordering correctly the hosts such as below by:
  - add vas with the user and the sk file for connection
  - order hosts

```yaml
all:
  vars:
    ansible_user: <USERNAME>
    ansible_ssh_private_key_file: ~/.ssh/master.pem
    
  hosts:
    k8s-m1:
      ansible_host: 172.31.255.141
      ip: 172.31.255.141
      access_ip: 172.31.255.141
    k8s-m2:
      ansible_host: 172.31.255.142
      ip: 172.31.255.142
      access_ip: 172.31.255.142
    k8s-m3:
      ansible_host: 172.31.255.143
      ip: 172.31.255.143
      access_ip: 172.31.255.143
    k8s-w1:
      ansible_host: 172.31.255.144
      ip: 172.31.255.144
      access_ip: 172.31.255.144
    k8s-w2:
      ansible_host: 172.31.255.145
      ip: 172.31.255.145
      access_ip: 172.31.255.145
    k8s-w3:
      ansible_host: 172.31.255.146
      ip: 172.31.255.146
      access_ip: 172.31.255.146
    k8s-w4:
      ansible_host: 172.31.255.147
      ip: 172.31.255.147
      access_ip: 172.31.255.147
  children:
    # here are the groups of hosts
    kube_control_plane:    
      hosts:
        k8s-m1:
        k8s-m2:
        k8s-m3:
    kube_node:
      hosts:
        k8s-m1:
        k8s-m2:
        k8s-m3:
        k8s-w1:
        k8s-w2:
        k8s-w3:
        k8s-w4:
    etcd:
      hosts:
        k8s-m1:
        k8s-m2:
        k8s-m3:
    k8s_cluster:
      children:
        kube_control_plane:
        kube_node:
    calico_rr:
      hosts: {}
```

4. Edit the `inventory/<MY_CLUSTER>/group_vars/k8s_cluster/addons.yml`

> OBS: For MetalLB obtain a range of free IPs

```yaml
              # dashboard
              dashboard_enabled: true

              # helm
              helm_enabled: true

              # metrics
              metrics_server_enabled: true

              # ingress
              ingress_nginx_enabled: true
              ingress_nginx_host_network: true

              #metallb
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

> OBS: If MetalLB is enabled as above then edit the `inventory/<MY_CLUSTER>/group_vars/k8s_cluster/k8s-cluster.yml` file and set `kube_proxy_strict_arp: true`


## Check configuration of target hosts

```bash
ssh -i ~/.ssh/master.pem <USERNAME>@<IP1>
sudo su
```

If `sudo su` will require password you either need to add the user to the sudoers file or to add `ansible_sudo_pass: "<PASSWORD>"` to the hosts file.


## The actual run

Now you can run the kubespray playbooks

```bash
$ ansible-playbook cluster.yml -i inventory/<MY_CLUSTER>/hosts.yml --become-user=root --become
```
> OBS: both --become-user=root and --become are required to run the playbooks as root

You can re-run it as many times as you want to fix any issues that may arise based on the Ansible idempotency capability.
