## Proxy Server Project

## Overview
This project is a simple proxy server implemented in Python. It receives HTTP requests from clients, checks if the requested resources are cached locally, and serves the cached content if available. If not, it fetches the requested resources from the origin server, caches them for future requests, and then serves the client. The proxy server handles HTTP GET requests and supports basic caching mechanisms.

## Features
HTTP GET Requests: Handles HTTP GET requests from clients.
Caching: Caches the fetched resources locally to reduce latency for future requests.
Error Handling: Provides basic error handling for 404 Not Found and other server errors.
Logging: Logs requests and responses for debugging and monitoring purposes.


## Requirements
Python 3.x
Socket library (comes with Python standard library)
urllib.parse (comes with Python standard library)
pathlib (comes with Python standard library)

## Error Handling
404 Not Found: If the requested resource is not found on the origin server, a 404 response is sent to the client.
500 Internal Error: If there is an error connecting to the origin server, a 500 response is sent to the client.
Other Errors: Any other errors result in an "UNSUPPORTED ERROR" response.