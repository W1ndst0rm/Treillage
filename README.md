Unofficial Wrapper library for the Filevine API
====================================
[![PyPI version](https://badge.fury.io/py/treillage.svg)](https://pypi.org/project/treillage)
[![Maintainability](https://api.codeclimate.com/v1/badges/1c532739b0c748e39242/maintainability)](https://codeclimate.com/github/W1ndst0rm/Treillage/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/1c532739b0c748e39242/test_coverage)](https://codeclimate.com/github/W1ndst0rm/Treillage/test_coverage)
![Tests](https://github.com/W1ndst0rm/Treillage/workflows/Tests/badge.svg)

*Treillage (tre-ˈyäzh): A lattice or framework for supporting vines.*

Treillage is an unofficial wrapper library for the Filevine API written in python.
This library is neither supported by or maintained by Filevine, Inc.

[Filevine's API Documentation](https://developer.filevine.io/v2/overview)

Key Features
============
* Leverages asyncio to speed up IO bound requests
* Automatically refreshes session authentication tokens
* Built-in token bucket rate limiting
* API endpoints with built-in pagination

Table of contents
=================

<!--ts-->
* [Installation](#library-installation)
* [Getting Started](#getting-started)
    * [Using built-in endpoints](#using-built-in-endpoints)
    * [Using raw HTTP methods](#using-raw-http-methods)
    * [Base URL](#base-url)
* [Rate Limiting and Connection Management](#Rate-Limiting-and-Connection-Management)
* [Exceptions](#exceptions)
    * [TreillageHTTPException](#treillagehttpexception)
    * [TreillageRateLimitException](#treillageratelimitexception)
    * [TreillageTypeError](#treillagetypeerror)
    * [TreillageValueError](#treillagevalueerror)
* [Examples](#examples)
<!--te-->
## Library Installation
```shell script
pip install treillage
```

Getting Started
=================
The only required parameter is a path to a yaml credentials file with the following keys: `key`, `secret`, `queueid`.
It should look like this:
```yaml
key: "fvpk_************************"
secret: "fvsk_***********************************"
queueid: "***********"
``` 
These values are obtained from the [Filevine developer portal](https://portal.filevine.io/).
The treillage module uses these credentials to obtain the accessToken and refreshToken for the authorization header.
These tokens are refreshed as needed throughout script execution. 

 
Using built-in endpoints
------------------------
```python
from treillage import Treillage
from treillage.endpoints import get_contact_list

async with Treillage(credentials_file="creds.yml") as tr:
    async for contact in get_contact_list(tr.conn, fields=['fullName', 'personId'], first_name='James'):
        print(contact['fullName'])
```
This will request the `personId` and `fullName` fields for all contacts with the first name of 'James'.

Using raw HTTP methods
----------------------
If there isn't a function written for the built-in endpoint you need, you can still use the rate limiting
and credential rotation features
```python
from treillage import Treillage

async with Treillage(credentials_file="creds.yml") as tr:
    query_parameters = {'requestedFields': ['fullName, personId'], 'firstName': 'James', 'offset': 0, 'limit': 50}
    contacts = await tr.conn.get(endpoint='/core/contacts', params=query_parameters)
    for contact in contacts:
        print(contact['fullName'])
```
This will request the `personId` and `fullName` fields for the first 50 contacts with the first name of 'James'.

POST and DELETE work similarly

```python
from treillage import Treillage

async with Treillage(credentials_file="creds.yml") as tr:
  # POST Example
  body = {
    'firstName': 'John',
    'lastName': 'Doe',
    'fullName': 'John Doe',
    'gender': 'M',
    'personTypes': ['Client']
  }
  response = await tr.conn.post(endpoint='/core/contacts', body=body)
  # DELETE Example
  await tr.conn.delete(endpoint='/core/documents/1234')
```

Base URL
--------
The base url for the server defaults to United States server at https://api.filevine.io.
To access the Canada specific server pass in the base_url parameter
```python
from treillage import Treillage, BaseURL

# Use the built-in Enum
async with Treillage(credentials_file="creds.yml", base_url=BaseURL.CANADA) as tr:

# Pass in a string
async with Treillage(credentials_file="creds.yml", base_url='https://api.filevine.ca') as tr:
```

Rate Limiting and Connection Management
======================================= 
The built-in rate limiter uses a token bucket technique. Each  web request consumes a token,
and tokens regenerate at a set rate. The bucket has a fixed capacity to keep the initial burst of requests
from exceeding the rate-limit. To keep things simple, the maximum number of tokens is equal to the amount regenerated
in one second.

To use the built-in rate limiter, one additional parameters must be passed to the treillage object:
* `requests_per_second` sets how many tokens are regenerated per second.

If this parameter is not set, no rate-limiting will occur.
```python
async with Treillage(credentials_file="creds.yml", requests_per_second=10) as tr:
    tr.do_something()
```
Additionally, the rate limiter will use an exponential backoff algorithm to
temporarily slow down requests when the server returns a HTTP 429 error (Rate Limit Exceeded). 

Alternatively the total number of simultaneous connections to the server can limited by passing
the `max_connections` parameter. If `max_connections` is not set, the default value of `100` will be used.

If you want to automatically retry a rate limited call, use the `@retry_on_rate_limit` decorator to wrap the function
you want to be retried.
```python
@retry_on_rate_limit
async def get_some_data(tr: Treillage, endpoint):
    return await tr.conn.get(endpoint)

some_data = await get_some_data(tr, '/some_data')
```

Exceptions
==========
The treillage module includes several exceptions to make error handling easier.
All exceptions inherit from `TreillageException`.

TreillageHTTPException
---------------------
* Inherits from `TreillageException`
* This exception is raised when the API returns any non 200 status code. 
* Parameters:
    * code - The HTTP error code
    * url - The url accessed
    * msg - The body of the server response or `"Received non-2xx HTTP Status Code {code}"`

TreillageRateLimitException
--------------------------
* Inherits from `TreillageHTTPException`
* This exception is raised when the API returns a 429 status code (Rate Limit Exceeded). 
* Parameters:
    * code - The HTTP error code. *It will always be 429*
    * url - The url accessed
    * msg - The body of the server response or `"Received non-2xx HTTP Status Code 429"`

TreillageTypeError
-----------------
* Inherits from `TreillageException` and `TypeError`
* Raised when a parameter for an endpoint does not match the required type
* Parameters
    * msg

TreillageValueError
------------------
* Inherits from `TreillageException` and `ValueError`
* Raised when a parameter for an endpoint does not meet the requirements in the endpoint specification.
For example, a contact's personTypes must be in the list `['Adjuster', 'Attorney', 'Client', 'Court',
'Defendant', 'Plaintiff', 'Expert', 'Firm', 'Insurance Company', 'Involved Party', 'Judge', 'Medical Provider']`
* Parameters:
    * msg
    
Examples
========
The [examples](examples/README.md) folder contains complete non-trivial examples of this module in use.
