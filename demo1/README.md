# Local tests


https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3




/var/lib/k8s-pvs/redis-storage-redis-slave-1/pvc-4ec7d473-e326-41df-8c93-0542f2091e68
/var/lib/k8s-pvs/redis-storage-redis-slave-0/pvc-0731f096-2ea3-4320-a736-ead7c367aee7

# Source: hg2/templates/redis-master.yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-master
  labels:
    app: redis
    role: master
    helm.sh/chart: hg2-0.1.0
    app.kubernetes.io/name: hg2
    app.kubernetes.io/instance: hg
    app.kubernetes.io/version: "0.1.0"
    app.kubernetes.io/managed-by: Helm
spec:
  type: ClusterIP
  selector:
    app: redis
    role: master
    app.kubernetes.io/name: hg2
    app.kubernetes.io/instance: hg
  ports:
  - port: 6379
    targetPort: redis-server

# Source: hg2/templates/redis-master.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-master
  labels:
    app: redis
    role: master
    helm.sh/chart: hg2-0.1.0
    app.kubernetes.io/name: hg2
    app.kubernetes.io/instance: hg
    app.kubernetes.io/version: "0.1.0"
    app.kubernetes.io/managed-by: Helm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
      role: master
  serviceName: ""
  template:
    metadata:
      labels:
        app: redis
        role: master
    spec:
      containers:
      - env:
        - name: SAVE_INTERVAL
          value: "60 1"
        - name: KUBERNETES_CLUSTER_DOMAIN
          value: "cluster.local"
        image: redis:5.0.5
        name: redis-master
        ports:
        - containerPort: 6379
          name: redis-server
        resources: {}
        volumeMounts:
        - mountPath: /data
          name: redis-storage
  updateStrategy: {}
  volumeClaimTemplates:
  - metadata:
      creationTimestamp: null
      name: redis-storage
    spec:
      accessModes:
      - ReadWriteOnce
      resources: 
        requests:
          storage: 1Gi
      volumeName: hg-hg2-master-pv    