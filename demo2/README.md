To set up the described application ecosystem in Kubernetes with autoscaling, you'll need several components:

1. **Node.js Application Deployment**:
   - A Kubernetes Deployment for the Node.js application.
   - A Service to expose the application.

2. **PostgreSQL Database**:
   - A Deployment or StatefulSet for PostgreSQL.
   - A Service for database access.

3. **Redis Service**:
   - A Deployment or StatefulSet for Redis.
   - A Service to access Redis.

4. **Horizontal Pod Autoscaler (HPA)**:
   - An HPA resource to scale the Node.js application based on load (CPU/Memory usage or custom metrics).

### Example Configuration:

#### 1. Node.js Application Deployment

```yaml
### 1. Base Node.js Application Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nodejs-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nodejs-app
  template:
    metadata:
      labels:
        app: nodejs-app
    spec:
      containers:
      - name: nodejs-app
        image: your-nodejs-app-image
        ports:
        - containerPort: 8080
        env:
          - name: POSTGRES_URL
            value: postgres-service
          - name: REDIS_URL
            value: redis-service
---
apiVersion: v1
kind: Service
metadata:
  name: nodejs-app-service
spec:
  type: ClusterIP
  selector:
    app: nodejs-app
  ports:
    - protocol: TCP
      port: 8080
---
#### 2. PostgreSQL Database
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:latest
        env:
          - name: POSTGRES_DB
            value: yourdatabase
          - name: POSTGRES_USER
            value: youruser
          - name: POSTGRES_PASSWORD
            value: yourpassword
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
    - protocol: TCP
      port: 5432
---
#### 3. Redis Service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:latest
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  type: ClusterIP
  selector:
    app: redis
  ports:
    - protocol: TCP
      port: 6379
---
#### 4. Horizontal Pod Autoscaler (HPA)
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: nodejs-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nodejs-app
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

then you can run above `combined-config.yaml` with:
```bash
kubectl apply -f combined-config.yaml
```
### Notes:

- Update `your-nodejs-app-image` to your actual Node.js application Docker image.
- Configure the database credentials and names in the PostgreSQL deployment.
- Ensure the Node.js application is configured to use environment variables for database connections.
- The HPA scales the Node.js application based on CPU utilization. Modify the thresholds as per your application's requirements.
- These configurations are basic and might need to be adjusted for security, persistence (for databases), and other operational considerations.

This setup provides a scalable Node.js application with a PostgreSQL database and Redis, managed and autoscaled by Kubernetes.