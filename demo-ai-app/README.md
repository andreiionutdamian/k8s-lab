# Demo/Tutorial ecosystem


Goal:
 - Access via 79.119.87.166:5080
 - Use postman to request a inference based on json POST


Setup:
 - Python monitor app (1 replica) deployment downloads model (Deployment)
    - uses Redis to announce update
 - Python serving app (4 replicas) StatefulSet 
    - loads models from PV and serves using GPU
    - uses Redis to get models
    - Saves on PostgreSQL request and response
 - Redis deployment stateless
 - Postgres sfs/deployment 1 or maybe more 


Steps:
 1. Write 2 scripts
 2. Write all k8s manifests (yamls)
    2.1. Monitor:
        - Deployment
        - Service
        - PV
        - PVC
        - Secret
    2.2. Serving:
        - SFS
        - Service
        - PV
        - PVC
        - Secret
        - ConfigMap
        - Ingress
    2.3. Redis:
        - Deployment
        - Service
        - Secret
    2.4. PostgreSQL:
        - Deployment
        - Service
        - PV
        - PVC
        - Secret
  3. Deploy & test
  4. Helmify
  5. Redeploy with helm
