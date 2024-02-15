#!/bin/bash
sed -i 's/\["ingress-controller-leader-{{ ingress_nginx_class }}"\]/\["ingress-controller-leader-{{ ingress_nginx_class }}","ingress-controller-leader"\]/g' roles/kubernetes-apps/ingress_controller/ingress_nginx/templates/role-ingress-nginx.yml.j2
