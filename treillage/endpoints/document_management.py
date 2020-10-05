from typing import List
from .. import ConnectionManager
from .list_paginator import list_paginator


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                              Documents
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

async def get_document(connection: ConnectionManager,
                       document_id: str,
                       requested_fields: List[str] = None):
    endpoint = f"/core/documents/{document_id}"
    params = dict()
    if requested_fields:
        fields = ','.join(*[requested_fields])
        params['requestedFields'] = fields

    return await connection.get(endpoint, params)


async def get_document_list(connection: ConnectionManager,
                            requested_fields: List[str] = None,
                            folder_id: str = None):
    endpoint = "/core/documents/"

    params = dict()
    if requested_fields:
        fields = ','.join(*[requested_fields])
        params['requestedFields'] = fields
    if folder_id:
        params['folderId'] = folder_id

    async for document in list_paginator(connection, endpoint, params):
        yield document


async def delete_document(connection: ConnectionManager,
                          document_id: str):
    endpoint = f"/core/documents/{document_id}"
    await connection.delete(endpoint)
