# EMQX deployment on k8s

## Prerequisites
- Helm
- Kubernetes

### Install dependencies with Helm
```bash
helm repo add jetstack https://charts.jetstack.io && \
  helm repo add emqx https://repos.emqx.io/charts && \
  helm repo update
```

### Install Cert-Manager
```bash
helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true
```

#### Check if the cert-manager is installed
```bash
kubectl wait --for=condition=available --timeout=60s deployment/cert-manager -n cert-manager
```

### Install EMQX-Operator
```bash
helm upgrade --install emqx-operator emqx/emqx-operator \
  --namespace emqx-operator-system \
  --create-namespace
```

#### Check if the EMQX-Operator is installed
```bash
kubectl wait --for=condition=Ready pods -l "control-plane=controller-manager" -n emqx-operator-system --timeout=60s
```

### Configure EMQX broker
```yaml
spec:
  image: emqx:5.5
  config:
    data: |
      mqtt.max_packet_size = 10485760
```

**Note:** The `mqtt.max_packet_size` is set to 10MB

### Configure EMQX broker **CORE** nodes and resources
```yaml
  coreTemplate:
    spec:
      replicas: 2
      resources:
        requests:
          cpu: 250m
          memory: 512Mi
```

### Configure EMQX broker **REPLICANT** nodes and resources
```yaml
    replicantTemplate:
    spec:
      replicas: 1
      resources:
        requests:
          cpu: 250m
          memory: 1Gi
```

### Configure EMQX broker listener service
```yaml
  listenersServiceTemplate:
    spec:
      type: LoadBalancer
```

### Configure EMQX broker dashboard service
```yaml
    dashboardServiceTemplate:
    spec:
      type: ClusterIP
```

**Note:** the service type can be:
* `LoadBalancer`
* `NodePort`
* `ClusterIP`

## Example ingress for EMQX Dashboard
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: emqx-dashboard-ingress
  namespace: custom-namespace
spec:
  ingressClassName: nginx
  rules:
    - host: mqtt-dashboard.k8s.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: emqx-dashboard
                port:
                  number: 18083
```