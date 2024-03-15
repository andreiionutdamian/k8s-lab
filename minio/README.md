# Minio deployment on k8s
## The following guide applies to a single node MinIO deployment on Kubernetes.

## Prerequisites
- Kubernetes

### Configure MINIO container
```yaml
spec:
  containers:
    - name: minio
      image: minio/minio:RELEASE.2023-09-20T22-49-55Z.hotfix.04ec67161
      args:
        - server
        - /data
        - --console-address
        - ":9001"  # Specify static console port
```

***Note:*** The `RELEASE.2023-09-20T22-49-55Z.hotfix.04ec67161` is the latest stable release of minio. You can find the latest release [here](https://hub.docker.com/r/minio/minio/tags?page=1&ordering=last_updated)

***Note:*** Please note the `--console-address` flag is used to specify the static console port. This is required to access the MinIO console.

### Configure MINIO container ports
```yaml
  ports:
    - containerPort: 9000
    - containerPort: 9001  # Expose the static console port
```

### Configure MINIO container volume
```yaml
  volumeMounts:
    - name: minio-persistent-storage
      mountPath: /data
```

***Note:*** The `minio-persistent-storage` is the persistent volume claim that is used to store the data.

***Note:*** The `mountPath` is the path where the data will be stored.