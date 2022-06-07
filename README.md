# python-gotify

[![PyPI](https://img.shields.io/pypi/v/gotify.svg?logo=pypi)](https://pypi.python.org/pypi/gotify)
[![Python](https://img.shields.io/pypi/pyversions/gotify.svg?logo=python)](https://pypi.python.org/pypi/gotify)
[![License](https://img.shields.io/pypi/l/gotify.svg)](https://pypi.python.org/pypi/gotify)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
![CI](https://github.com/d-k-bo/python-gotify/actions/workflows/ci.yml/badge.svg)
[![Codecov](https://img.shields.io/codecov/c/github/d-k-bo/python-gotify)](https://app.codecov.io/gh/d-k-bo/python-gotify)

python-gotify is a python client library to interact with your [gotify](https://github.com/gotify/server) server without having to handle requests manually.

It offers both a synchronous and an asynchronous interface powered by [httpx](https://www.python-httpx.org/).
Optionally, push messages can be received via websockets.

## Installation

python-gotify can be installed from [PyPi](https://pypi.org/project/gotify/) using pip:

```
pip install gotify
```

If you want to listen to push messages, the additional dependency on [websockets](https://websockets.readthedocs.io/en/stable/) can be installed with

```
pip install gotify[stream]
```

## Usage

To send messages:

```python
from gotify import Gotify

gotify = Gotify(
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
from gotify import Gotify

gotify = Gotify(
    base_url="https://gotify.example.com",
    client_token="CoLwHBCAr8z2MMA",
)

app = gotify.create_application("foobar", description="test application")

print("Created new application:", app)
```

would result in

```plain
Created new application: {'id': 42, 'token': 'ArHD_yGYf63-A13', 'name': 'foobar', 'description': 'test application', 'internal': False, 'image': 'static/defaultapp.png'}
```

**Note:** For most things you need to create a new client and set `client_token` accordingly.

This library tries to implement every endpoint of the gotify API as an instance method of the `Gotify` class.

More details about the capabilities of gotify's API can be found in its [API documentation](https://gotify.net/api-docs).

**Note:** since I don't use any gotify plugins, plugin-related functions are currently completely untested.

### Async Usage

python-gotify's asynchronous client works similar to the synchronous one, you just need to `await` all methods. It is recommended to use it as a context manager if you want to send multiple requests.

```python
import asyncio
from gotify import AsyncGotify

async def send_message_async():
    async_gotify = AsyncGotify(
        base_url="https://gotify.example.com",
        app_token="AsWIJhvlHb.xgKe",
    )

    await async_gotify.create_message(
        "This message was sent asynchronously!",
        title="Hello Asynchronous World",
    )

asyncio.run(send_message_async())
```

### Reusing HTTP sessions

If you want to send multiple requests to a server you can use both `Gotify` and `AsyncGotify` as a (asynchronous) context manager which will use a single HTTP session to reduce some connection overhead.

```python
with Gotify(...) as gotify:
    ...

async with AsyncGotify(...) as async_gotify:
    ...
```

### Receive push messages via websockets

`AsyncGotify` implements gotify's `/stream` endpoint which allows to receive push messages via websockets. To use it make sure you installed python-gotify with `pip install gotify[stream]`.

`AsyncGotify.stream()` is implemented as an asynchronous generator that waits for incoming messages and yields `Message` dictionaries.

```python
import asyncio
from gotify import AsyncGotify

async def log_push_messages():
    async_gotify = AsyncGotify(
        base_url="https://gotify.example.com",
        client_token="CoLwHBCAr8z2MMA",
    )

    async for msg in async_gotify.stream():
        print(msg)

asyncio.run(log_push_messages())
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please use [nox](https://nox.thea.codes/en/stable/tutorial.html#installation) to format, lint, type-check and test your code by calling `nox` in your project directory.

The test suite downloads a server binary and starts a preconfigured test server on port 30080 (this doesn't work on MacOS). If you encounter issues starting the test server, please create an issue.

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for more information.
