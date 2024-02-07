# Insights


## Install stuff

https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3



## Helmify issues

### StatefulSet

In this case we have a statefulset that is not correctly helmified in the target `sf` chart. Basically the selectorLabels are not added to the selector section of the statefulset. This is a problem because the service will not be able to find the pods as the pods will have different labels than the StatefulSet.

```yaml
kind: StatefulSet
metadata:
  name: {{ include "sf.fullname" . }}-slave
  labels:
    app: redis
    role: slave
  {{- include "sf.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.slave.replicas }}
  selector:
    matchLabels:
      app: redis
      role: slave
    # here helmify did not correctly add the selectorLabels
    # thus we need to add them manually otherwise the pods will not
    # have the correct labels and the service will not be able to find them
    {{- include "sf.selectorLabels" . | nindent 6 }}
  serviceName: ""
  template:
    metadata:
      labels:
        app: redis
        role: slave
      # here helmify did not correctly add the selectorLabels
      # thus we need to add them manually otherwise the pods will not
      # have the correct labels and the service will not be able to find them
      {{- include "sf.selectorLabels" . | nindent 8 }}    
```

This behaviour is not consistent as in the case of `Deployment` helmify correctly adds the selectorLabels to the selector section.

### Service

Another issue was related to the service. While the service template for the `master` was generated as
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "sf.fullname" . }}-master
```
in the `slave` case the service template was generated with wrong connection
```yaml
Containers:
  redis-slave:
    Container ID:  docker://9ad9bdd31e2d9c91edcbd1c0931979c89ac82cc84b2bbe33c40d33089e0169c6
    Image:         redis:5.0.5
    Image ID:      docker-pullable://redis@sha256:5dcccb533dc0deacce4a02fe9035134576368452db0b4323b98a4b2ba2d3b302
    Port:          6379/TCP
    Host Port:     0/TCP
    Command:
      /bin/sh
    Args:
      -c
      redis-server --slaveof redis-master 6379 --loglevel debug
```

so there is a name mismatch between the hard-coded service name and the generated service name. In this case we need to fix the service name in the template to match the generated service name.


### Redis stuff

Seems that redis slave is trying to bind to the same volume as the master. The first work-around was to deploy the slave as deployment rather than StatefulSet