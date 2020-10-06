from .. import ConnectionManager, TreillageRateLimitException


async def list_paginator(
        connection: ConnectionManager,
        endpoint: str,
        params: dict
):
    has_more = True
    params['offset'] = 0
    params['limit'] = 100

    while has_more:
        try:
            resp = await connection.get(endpoint, params)
            has_more = resp['hasMore']
            params['offset'] += params['limit']
            for item in resp['items']:
                yield item
        except TreillageRateLimitException:
            pass
