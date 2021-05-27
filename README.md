# python-gotify

This python module allows to manage and send messages to your [gotify server](https://github.com/gotify/server) without handling requests manually.

To send messages:

```python
import gotify

gotify.config(
    base_url="https://gotify.example.com",
    app_token="AsWIJhvlHb.xgKe",
)

gotify.create_message(
    "Hello you wonderful people!",
    title="Hello World",
    priority=0,
)
```

**Note:** To send messages you need to create a new application and set `app_token` accordingly.

You can also manage things like applications:

```python
import gotify

gotify.config(
    base_url="https://gotify.example.com",
    client_token="CoLwHBCAr8z2MMA",
)

app = gotify.create_application("foobar", description="test application")

print("Created new application:", app)
```

would result in

```plain
Created new application: {'id': 42, 'token': 'ArHD_yGYf63-A13', 'name': 'fooba
r', 'description': 'test application', 'internal': False, 'image': 'static/def
aultapp.png'}
```

**Note:** For most things you need to create a new client and set `client_token` accordingly.

More details about the capabilities of gotify's API can be found in its [API documentation](https://gotify.net/api-docs).

**Note:** since I don't use any gotify plugins, plugin-related functions are completely untested.
