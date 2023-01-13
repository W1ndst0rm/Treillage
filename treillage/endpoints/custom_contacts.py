
from typing import List, Dict
from .. import ConnectionManager
from .. import TreillageValueError
from .list_paginator import list_paginator


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                             Custom Contacts
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


async def create_custom_contact(
    connection: ConnectionManager,
    firstName: str,
    middleName: str = None,
    lastName: str = None,
    nickname: str = None,
    prefix: str = None,
    suffix: str = None,
    fromCompany: str = None,
    jobTitle: str = None,
    department: str = None,
    isSingleName: bool = None,
    isArchived: bool = None,
    isDeceased: bool = None,
    birthdate: str = None,
    deathdate: str = None,
    addresses: list = None,
    **kwargs
):
    arguments = locals().copy()
    body = list()
    def addAction(key, action, value):
        body.append({
            "selector": key,
            "action": action,
            "value": value
        })
    endpoint = f'/core/custom-contacts/'
    standardStringFields = 'firstName middleName lastName nickname prefix suffix fromCompany jobTitle department birthdate deathdate'.split()
    standardBoolFields = 'isSingleName isArchived isDeceased'.split()
    
    for key, value in arguments.items():

        if key in standardStringFields and value:
            addAction(key, 'UPDATE', value)

        if key in standardBoolFields and value:
            if isinstance(value, bool):
                addAction(key, 'UPDATE', value)
            else:
                raise TreillageValueError(
                    f"{key}: {value} is not a bool"
                )

        if key == 'addresses' and value:

            if not isinstance(value, List):
                raise TreillageValueError(
                    f"{key} must be a list."
                )
            addressFields = "line1 line2 city state zip notes".split()
            for address in value:

                if not isinstance(address, Dict):
                    raise TreillageValueError(
                        f"{key} must be a list of dictionaries"
                    )

                if not set(address.keys()).issubset(addressFields):
                    raise TreillageValueError(
                        f"Address includes invalid fields:" +
                        f"{[key for key in address.keys() if key not in addressFields]}"
                    )
                
                if 'state' in address.keys() and address['state']:
                    if len(address['state']) > 2:
                        raise TreillageValueError(
                            f"State field cannot be > 2 characters: " + address['state']
                        )
                
                addAction('addresses', 'ADD', address)
                
        #todo: add support for custom fields
        if key.startswith('custom.') and value:
            print("wow, a custom key!")

    return await connection.post(endpoint, body)

""""
body = {
    'firstName': 'Jake',
    'lastName': 'Mecham',
    'isDeceased': False,
    'addresses': [
        {
                "line1": "1242 Wilmington Ave",
                "line2": "#100",
                "city": "Salt Lake City",
                "state": "UT",
                "zip": "84106",
                "notes": "Filevine Headquarters!"
        }
    ]
}
create_custom_contact(**body)
"""
