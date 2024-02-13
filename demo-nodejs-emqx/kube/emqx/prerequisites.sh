#!/bin/bash

# This script installs the prerequisites for the EMQX Operator and cert-manager
# It adds the Jetstack Helm repository and installs cert-manager
# It also adds the EMQX Helm repository and installs the EMQX Operator

# Exit on error
set -e

echo -e "Update Helm repositories"
helm repo add jetstack https://charts.jetstack.io && \
 helm repo add emqx https://repos.emqx.io/charts && helm repo update

echo -e "Install cert-manager"
helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

echo -e "Wait for cert-manager to be ready"
kubectl wait --for=condition=available --timeout=600s deployment/cert-manager -n cert-manager

echo -e "Install the EMQX Operator"
helm upgrade --install emqx-operator emqx/emqx-operator \
  --namespace emqx-operator-system \
  --create-namespace

echo -e "Wait for EMQX Operator to be ready"
kubectl wait --for=condition=Ready pods -l "control-plane=controller-manager" -n emqx-operator-system --timeout=600s