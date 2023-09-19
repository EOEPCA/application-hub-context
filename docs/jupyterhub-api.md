# Using JupyterHub API

See [JupyterHub documentation](https://jupyterhub.readthedocs.io/en/stable/reference/rest-api.html) for more information on the JupyterHub API.

The code examples below show how the JupyterHub REST API can be used with Python and the `requests` module.

## Obtain an API token

In order to use the API, an API token must be obtained. This requires the username and password of an admin or other user with the necessary privileges.

```python
import requests

endpoint = "https://app-hub.acme.com/hub/api"

headers = {'Content-Type': 'application/json'}

data = {
  "username": "<username>"
  "password": "<password>"
}

r = requests.get(f"{endpoint}/authorizations/token", headers=headers, json=data, verify=False)

token = r.json()['token']
```

## Groups

### List groups

```python
import requests

endpoint = "https://app-hub.acme.com/hub/api"
token = "d...8"   # previously obtained API token

headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

r = requests.get(f"{endpoint}/groups", headers=headers, verify=False)

r.json()
```

### Create group

```python
import requests

endpoint = "https://app-hub.acme.com/hub/api"
token = "d...8"   # previously obtained API token

headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

group = 'group-a'

r = requests.post(f"{endpoint}/groups/{group}", headers=headers, verify=False)
r.status_code
r.json()
```

### Add user to group


```python
import requests

endpoint = "https://app-hub.acme.com/hub/api"
token = "d...8"   # previously obtained API token

headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

group = 'group-a'

data = {
  "users": ["mrossi"]
}

r = requests.post(f"{endpoint}/groups/{group}/users", headers=headers, json=data, verify=False)
r.status_code
```

### Remove user from group

```python
import requests

endpoint = "https://app-hub.acme.com/hub/api"
token = "d...8"   # previously obtained API token

headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

group = 'group-a'

data = {
  "users": ["mrossi"]
}

r = requests.delete(f"{endpoint}/groups/{group}/users", headers=headers, json=data, verify=False)

r.json()
```

## Named servers

### Create a named server

```python
import requests

endpoint = "https://app-hub.acme.com/hub/api"
token = "d...8"   # previously obtained API token

headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}

data = {"profile": "profile_1_slug"}

server_name = "labs"

user = "mrossi"
r = requests.post(f"{endpoint}/users/{user}/servers/{server_name}", headers=headers, json=data, verify=False)

r.status_code, r.text
```
