# OpenShift intro


| Term | Definition | Category |
|------|------------|----------|
| A/B testing | Strategy used for testing new features in front-end applications to evaluate two versions of the application. | Horizontal |
| Build | The process of transforming inputs into a resultant object. | Horizontal |
| BuildConfig | An OpenShift-specific object that defines the process for a build to follow. | OpenShift k8s extension |
| Canary Deployments | Deploying a new version of an application by gradually increasing the number of users. | Horizontal |
| Circuit breaking | A method to prevent errors in one microservice from cascading to other microservices. | Horizontal |
| Configuration Change | A trigger causing a new build to run when a new BuildConfig resource is created. | OpenShift k8s extension |
| Control Plane | Manages desired configuration and dynamically programs and updates proxy servers as the environment changes. | Horizontal |
| Custom build strategy | Requires defining and creating your own builder image. | OpenShift k8s extension |
| Custom builder images | Regular Docker images containing logic to transform inputs into expected outputs. | Horizontal |
| CRDs | Custom code defining a resource to add to your Kubernetes API server. | Horizontal |
| Custom controllers | Reconcile the custom resources (CRDs) actual state with its desired state. | Horizontal |
| Data plane | Handles communication between services, requiring a service mesh for traffic identification and decision-making. | Horizontal |
| Enforceability (Control) | Istio provides control by enforcing policies across a fleet, ensuring fair resource distribution. | Horizontal |
| Envoy proxy | A proxy used by service meshes to intercept network traffic. | Horizontal |
| Human operators | Understand the systems they control and know how to deploy services and fix problems. | Horizontal |
| Image Change | A trigger to rebuild a containerized application when a new or updated version of an image is available. | OpenShift k8s extension |
| ImageStream | An OpenShift abstraction for referencing container images. | OpenShift k8s extension |
| ImageStream Tag | An identity to the pointer in an ImageStream pointing to a certain image in a registry. | OpenShift k8s extension |
| Istio | A platform-independent service mesh platform often used with Kubernetes. | Horizontal |
| Man-in-the-middle attacks | A type of cyber-attack where the attacker secretly intercepts and relays messages between two parties. | Horizontal |
| Observability | Helps observe the traffic flow in your mesh, trace call flows, dependencies, and view metrics. | Horizontal |
| OpenShift | A hybrid cloud, enterprise Kubernetes application. | OpenShift k8s extension |
| OpenShift CI/CD process | Automates code merging, building, testing, approving, and deploying to different environments. | OpenShift k8s extension |
| Operators | Automate cluster tasks and act as a custom controller to extend the Kubernetes API. | Horizontal |
| Operator Framework | Tools and capabilities to deliver an efficient customer experience in managing Operators. | Horizontal |
| OperatorHub | A web console for cluster administrators to find Operators for installation. | OpenShift k8s extension |
| Operator Lifecycle Manager | Controls the install, upgrade, and RBAC of Operators in a cluster. | OpenShift k8s extension |
| Operator maturity model | Defines the phases of maturity for Operations activities. | Horizontal |
| Operator Pattern | A system design linking a Controller to one or more custom resources. | Horizontal |
| Operator Registry | Stores CRDs, CSVs, and Operator metadata for packages and channels. | OpenShift k8s extension |
| Operator SDK | Helps authors build, test, and package Operators. | Horizontal |
| postCommit | An optional build hook. | OpenShift k8s extension |
| Retries | A method to prevent errors in one microservice from affecting others. | Horizontal |
| runPolicy | Controls how builds from a build configuration need to run. | OpenShift k8s extension |
| Service Broker | Provides a process for operations like upgrades, failover, or scaling. | Horizontal |
| Service Mesh | A layer for secure and reliable service-to-service communication. | Horizontal |
| Software operators | Automate processes traditionally performed by human operators. | Horizontal |
| Source-to-Image | A tool for building reproducible container images. | OpenShift k8s extension |
| Source strategy | Shows the strategy used to execute the build. | Horizontal |
| Source type | Determines the primary input for a build. | Horizontal |
| Webhook | A trigger that sends requests to an API endpoint for automation. | Horizontal |
