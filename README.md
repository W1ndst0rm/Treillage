Wrapper library for the Filevine API
====================================
[API Documentation](https://developer.filevine.io/v2/overview)

Key Features
============
* Leverages asyncio to speed up IO bound requests
* Automatically refreshes session authentication tokens
* Built-in token bucket rate limiting
* API endpoints with built-in pagination

Table of contents
=================

<!--ts-->
* [Installation](#library-instalation)
* [Getting Started](#getting-started)
    * [Using built-in endpoints](#using-built-in-endpoints)
    * [Using raw HTTP methods](#using-raw-http-methods)
* [Rate Limiting and Connection Management](#Rate-Limiting-and-Connection-Management)
* [Exceptions](#exceptions)
    * [FilevineHTTPException](#FilevineHTTPException)
    * [FilevineRateLimitException](#FilevineRateLimitException)
    * [FilevineTypeError](#FilevineTypeError)
    * [FilevineValueError](#FilevineValueError)
<!--te-->
## Library Installation
```
pip install filevine
```

Getting Started
=================
The only required parameter is a path to the yaml credentials file from the [developer portal](https://portal.filevine.io/)
 
Using built-in endpoints
------------------------
```python
from filevine import Filevine
from filevine.endpoints import get_contact_list

async with Filevine(credentials_file="creds.yml") as fv:
    async for contact in get_contact_list(fv.conn, fields=['fullName', 'personId'], first_name='James'):
        print(contact['fullName'])
```
This will request the personId and fullName fields for all contacts with the first_name 'James'.
The full name of every contact is then printed to the console.

Using raw HTTP methods
----------------------
If there isn't a function written for the built-in endpoint you need, you can still use the rate limiting
and credential rotation features
```python
from filevine import Filevine

async with Filevine(credentials_file="creds.yml") as fv:
    query_parameters = {'requestedFields': ['fullName, personId'], 'firstName': 'James', 'offset': 0, 'limit': 50}
    contacts = await fv.conn.get(endpoint='/core/contacts', params=query_parameters)
    for contact in contacts:
        print(contact['fullName'])
```
This will request the personId and fullName fields for the first 50 contacts with the firstName of 'James'.

POST and DELETE work similarly
```python
from filevine import Filevine

async with Filevine(credentials_file="creds.yml") as fv:
    # POST Example
    body = {
        'firstName' : 'John',
        'lastName' : 'Doe',
        'fullName' : 'John Doe',
        'gender': 'M',
        'personTypes': ['Client'] 
    }
    response = await fv.conn.post(endpoint='/core/contacts', json=body)
    # DELETE Example
    await fv.conn.delete(endpoint='/core/documents/1234')
```

Rate Limiting and Connection Management
======================================= 
The built-in rate limiter uses a token bucket technique. Each  web request consumes a token,
and tokens regenerate at a set rate. The bucket has a fixed capacity to keep the initial burst of requests
from exceeding the rate-limit.

To use the built-in rate limiter, two parameters must be passed to the filevine object:
* `rate_limit_max_tokens` sets the capacity of the token bucket
* `rate_limit_token_regen_rate` sets how many tokens are regenerated per second.
```python
async with Filevine(credentials_file="creds.yml", rate_limit_max_tokens=10, rate_limit_token_regen_rate=10) as fv:
    fv.do_something()
```
Additionally, the rate limiter will use an exponential backoff algorithm to
temporarily slow down requests when the server returns a HTTP 429 error (Rate Limit Exceeded). 

Alternatively the total number of simultaneous connections to the server can limited by passing
the `max_connections` parameter or the default value of `100` will be used.

Exceptions
==========
The filevine module includes several exceptions to make error handling easier.
All exceptions inherit from `FilevineException`.

FilevineHTTPException
---------------------
* Inherits from `FilevineException`
* This exception is raised when the API returns any non 200 status code. 
* Parameters:
    * code - The HTTP error code
    * url - The url accessed
    * msg - The body of the server response or `"Received non-2xx HTTP Status Code {code}"`

FilevineRateLimitException
--------------------------
* Inherits from `FilevineHTTPException`
* This exception is raised when the API returns a 429 status code (Rate Limit Exceeded). 
* Parameters:
    * code - The HTTP error code. *It will always be 429*
    * url - The url accessed
    * msg - The body of the server response or `"Received non-2xx HTTP Status Code 429"`

FilevineTypeError
-----------------
* Inherits from `FilevineException` and `TypeError`
* Raised when a parameter for an endpoint does not match the required type
* Parameters
    * msg

FilevineValueError
------------------
* Inherits from `FilevineException` and `ValueError`
* Raised when a parameter for an endpoint does not meet the requirements in the endpoint specification.
For example, a contact's personTypes must be in the list `['Adjuster', 'Attorney', 'Client', 'Court',
'Defendant', 'Plaintiff', 'Expert', 'Firm', 'Insurance Company', 'Involved Party', 'Judge', 'Medical Provider']`
* Parameters:
    * msg

