# ToDo

  - [ ] add HuggingFace support
    - [ ] download
    - [ ] serving
  - [ ] CI/CD complete

## Traian

  - [ ] add monitor Deployment and serving StatefulSet (carefull with Ingress path overwrite)
  - [ ] complete monitor_app.py `maybe_init_models`
  - [ ] complete serving_app.py `__get_k8s_status` using kube_mixin.py
  - [ ] refactor manifests with shorter names
  - [ ] setup RBAC for kube_mixin.py
  - [ ] fix PV vs env 

