# Using JupyterHub API

The [JupyterHub REST API](https://jupyterhub.readthedocs.io/en/stable/reference/rest-api.html) provides programmatic access to many of JupyterHub’s core functions — including user and group management, server control, and more. This allows administrators and automation tools to manage JupyterHub instances efficiently.

This section outlines how to interact with the JupyterHub API using Python and the `requests` library, with practical examples to handle tasks such as:

- Authenticating and retrieving an API token
- Managing user groups (create, list, add/remove users)
- Starting named servers for specific users

---

## Overview

The following Python snippets demonstrate how to interact with key features of the JupyterHub API:

- **API Token Retrieval** : Authenticate using a username/password and receive a token for further use 
- **Group Management**: Create, list, and modify user groups                                        |
- **Named Server Control**: Launch Jupyter environments tied to specific users and profiles            |



## 1. API Token Retrieval

Before accessing the API, you must obtain an access token by authenticating with valid credentials. This token is required for all subsequent requests.

```python
r = requests.get(f"{endpoint}/authorizations/token", headers=headers, json=data)
```

> ⚠️ This method may depends on your JupyterHub authenticator setup (e.g., OAuth, native password, etc.).


## 2. Group Management

The group API allows administrators to organize users into logical groups for resource or permission control.

### a. List Existing Groups

```python
r = requests.get(f"{endpoint}/groups", headers=headers)
```

### b. Create a New Group

```python
r = requests.post(f"{endpoint}/groups/{group}", headers=headers)
```

### c. Add Users to a Group

```python
r = requests.post(f"{endpoint}/groups/{group}/users", headers=headers, json=data)
```

### d. Remove Users from a Group

```python
r = requests.delete(f"{endpoint}/groups/{group}/users", headers=headers, json=data)
```


## 3. Named Server Management

You can create named servers tied to specific profiles. This is useful for launching custom environments under user control.

### Create a Named Server for a User

```python
r = requests.post(f"{endpoint}/users/{user}/servers/{server_name}", headers=headers, json=data)
```
