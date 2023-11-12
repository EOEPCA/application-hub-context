# Kubernetes configuration

JupyterHub is configured to run the pods in a dedicated workspace.

As such, a ClusterRole is needed with the manifest:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: jupyter-rbac
subjects:
  - kind: ServiceAccount
    name: hub
    namespace: jupyter
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
```

Download the manifest from:

[cluster-role-binding.yaml](./cluster-role-binding.yaml){:download}

Apply with:

```
kubectl apply -f cluster-role-binding.yaml
```

or do:

```
curl https://eoepca.github.io/application-hub-context/cluster-role-binding.yaml | kubectl apply -f -
```
