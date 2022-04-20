### steps to provision a Kubernetes cluster

1. install required packages
```shell
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-add-repository "deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib"
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
sudo apt update
sudo apt install vagrant
sudo apt install virtualbox-6.1

cat > /etc/vbox/networks.conf <<EOF
* 10.0.0.0/8
* 172.16.0.0/8
* 192.168.0.0/16
* 2001::/64
EOF
```

2. Edit Vagrantfile to change each VM's resource amount. [Optional]

3. Let vagrant provision the cluster. Run the bellow command and wait to finish ([adapted from here](https://www.youtube.com/watch?v=wPdIBeWJJsg)).
```shell
vagrant up
```

4. create .kube folder to store kubernetes cluster configuration.
```shell
mkdir ~/.kube
```
5. Copy kubernetes config file to your host machine. use *admin* as password when prompt.
```shell
scp root@kube_master:/etc/kubernetes/admin.conf ~/.kube/config
```

6. Check if IP address of nodes are correctly set (IP for each node be the same specified in Vagrantfile)
```shell
kubectl get nodes -o wide
```
> If it's not correctly set, follow [this](https://github.com/kubernetes/kubernetes/issues/63702#issuecomment-554277862).
> Edit /etc/systemd/system/kubelet.service.d/10-kubeadm.conf for each node and set IP of each one.

7. Install metrics-server in cluster [Optional]
   
    7.1. Get yaml file
   ```shell
    wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    ```
   
    7.2. Open components.yaml file with and editor, find metrics-server Deployment section, add --kubelet-insecure-tls 
    to containers -args
   
    7.3. kubectl apply -f components.yaml
