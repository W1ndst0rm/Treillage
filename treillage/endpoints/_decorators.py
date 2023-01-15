from .. import ConnectionManager
from typing import AsyncGenerator, Coroutine, List
from .list_paginator import list_paginator

# Make sure to add this decorator before the get_item/get_item_list decorator
def requested_fields(func):
    def wrapper(*args, **kwargs):
        params = kwargs.setdefault("params", dict())
        if kwargs.get("requested_fields"):
            requested_fields = ",".join(*[kwargs.get("requested_fields")])
            params["requestedFields"] = requested_fields
        return func(*args, **kwargs)

    return wrapper


def get_item(func):
    async def wrapper(connection: ConnectionManager, *args, **kwargs) -> dict:
        params = kwargs.setdefault("params", dict())
        endpoint = func(connection, *args)
        return await connection.get(endpoint, params)

    return wrapper


def get_item_list(func):
    async def wrapper(connection: ConnectionManager, *args, **kwargs) -> AsyncGenerator:
        params = kwargs.setdefault("params", dict())
        endpoint = func(connection, *args)
        async for item in list_paginator(connection, endpoint, params):
            yield item

    return wrapper
