# Introduction with Kubernetes with FastAPI and Redis

This is a basic example of a FastAPI application with Redis as a backend. The application is containerized and deployed to a Kubernetes cluster. In order to use `start1.sh` / `start2.sh`, `stop1.sh` / `stop2.sh`, etc. scripts, you need to first configure the namespaces and the secrets.

## Namespaces

```bash
kubectl apply -f ns.yaml
```

## Secrets

Copy `.secret.yaml` to `secrets.yaml` and fill in the base64 encoded values. Then apply the secrets to the cluster with the following command:

```bash
kubectl apply -f secrets.yaml
```

## Tests

Finally you can run the full tests by changing to either `nodeport_examples` or `production_like` dirs and run the following command:

```bash
./test_nodeport.sh
```

or 
```bash
./test_with_ingress.sh
```