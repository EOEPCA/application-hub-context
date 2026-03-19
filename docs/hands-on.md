# Hands-on

## 1. Generate your config

Install and use the external configurator project:

- PyPI: [https://pypi.org/project/app-hub-configurator/](https://pypi.org/project/app-hub-configurator/)
- Docs: [https://eoepca.github.io/app-hub-configurator/](https://eoepca.github.io/app-hub-configurator/)

Produce a `config.yaml` file containing your target profiles.

## 2. Place the generated config in this repository

Copy or rename the generated file to `custom-config.yml` in the repository root:

```bash
cp config.yaml custom-config.yml
```

The `skaffold` `custom` profile is already configured to use this file.

## 3. Deploy with skaffold

```bash
skaffold run -p custom
```

## 4. Verify deployment

```bash
kubectl get pods -n jupyter
kubectl get configmap -n jupyter
```
