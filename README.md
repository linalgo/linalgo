![main](https://github.com/linalgo/linalgo/actions/workflows/main.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![PyPI - Version](https://img.shields.io/pypi/v/linalgo)


# Linalgo W3C Web Annotation Library

Linalgo is a Python module to help Machine Learning team create and curate 
datasets for Natural Language Processing. It tries to follow
the W3C [Web Annotation Data Model](https://www.w3.org/TR/annotation-model/) and
to provides a powerful system to add metadata to most commonly used text and
image formats: TXT, PDF, HTML, etc.

## Documentation

The documentation is available at [https://linalgo.github.io/linalgo](https://linalgo.github.io/linalgo/)

## Installation 

Basic installation:
```
pip install linalgo
```

To use the annotation server functionality:
```
pip install "linalgo[hub]"
```

## Linalgo CLI

Linalgo provides a command-line interface to interact with the annotation server (linhub) and manage your configuration.

### Getting Started

Initialize your environment with interactive prompts:
```
linalgo init
```

This will:
- Set up your username and organization
- Configure the server URL
- Initialize a local server if using localhost
- Log you in and save your authentication token

### Authentication

Log in to the Linalgo hub and save your authentication token:
```
linalgo login
```

### Configuration Management

Manage your configuration settings:
```
linalgo config show            # Show all configuration values
linalgo config get <key>       # Get a specific configuration value
linalgo config set <key> <value>  # Set a configuration value
linalgo config load [env_file]    # Load configuration from .env file
```

### Interacting with the Hub

Pass commands directly to linhub:
```
linalgo hub <command>
```

For example, to start the annotation server:
```
linalgo hub runserver
```

## Running the Annotation Server

After installing with the hub extras, you can run a local annotation server using:
```
linalgo hub runserver
```

This will start a local Django server that you can use for annotation tasks.

## Test

```
pytest
```

## Storing Annotation Data

By default, linalgo stores annotations on a dedicated hub at https://hub.linalgo.com.
There are also connectors to retrieve data from Google BigQuery.
