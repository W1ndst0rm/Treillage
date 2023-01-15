from .. import ConnectionManager
from ._decorators import get_item, post_item
from ..classes import Contact


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                             Custom Contacts
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


@get_item
async def get_contact_metadata(connection: ConnectionManager):
    return f"/core/custom-contacts-meta"


@post_item
async def create_custom_contact(connection: ConnectionManager, contact=Contact):
    return f"/core/custom-contacts", contact.build_body_custom()
