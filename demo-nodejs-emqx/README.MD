# demo-nodejs-emqx

### Prerequisites
- Helm
- Kubernetes

### Install EMQX
```bash
cd emqx && ./prerequisites.sh
```

### Install the application stack
```bash
cd kube && \
kubectl apply -f namespace.yml && \
kubectl apply -f secret.yml && \
kubectl apply -f minio.yml && \
kubectl apply -f emqx/eqmx.yml && \
kubectl apply -f application-1.yml && \
kubectl apply -f application-2.yml
```

### Configure EMQX broker
- Login with the default credentials `admin:public`
- Create a new user

### Configure MinIO storage
- Login with credentials provided in `secret.yml`
- Create a new bucket `demo-nodejs-emqx`

For development purposes, you can use the MinIO web interface using the domain name `http://minio-console.k8s.local`

