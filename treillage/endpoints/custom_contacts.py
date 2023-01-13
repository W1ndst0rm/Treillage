
from typing import List, Dict
from .. import ConnectionManager
from .. import TreillageValueError
from .list_paginator import list_paginator


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                             Custom Contacts
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

async def get_contact_metadata(
        connection: ConnectionManager,
        fields: List[str] = None
):
    endpoint = f'/core/custom-contacts-meta'
    params = dict()
    if fields:
        requested_fields = ','.join(*[fields])
        params['requestedFields'] = requested_fields
    sessionMetadata = await connection.get(endpoint, params)
    return sessionMetadata


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
    addresses: List[dict] = None,
    metadata: List[dict] = None,
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
            addressFields = "line1 line2 city state zip notes addressLabelID addressLabel".split()
            for address in value:

                if not isinstance(address, Dict):
                    raise TreillageValueError(
                        f"'addresses' must be a list of dictionaries"
                    )

                if not set(address.keys()).issubset(addressFields):
                    raise TreillageValueError(
                        f"Address includes invalid fields:" +
                        f"{address.keys()}"
                    )

                if address.get('state'):
                    if len(address['state']) > 2:
                        raise TreillageValueError(
                            f"State field cannot be > 2 characters: " +
                            address['state']
                        )

                if metadata:
                    addressLabelAllowedValues = next(
                        item for item in metadata if item["selector"] == "addresses")['allowedValues']

                    if address.get('addressLabelID'):
                        if not address['addressLabelID'] in [x['addressLabelID'] for x in addressLabelAllowedValues]:
                            raise TreillageValueError(
                                f"addressLabelID is not valid: {address['addressLabelID']}"
                            )

                    if address.get('addressLabel'):
                        if address['addressLabel'] in [x['name'] for x in addressLabelAllowedValues]:
                            address['addressLabelID'] = next(
                                item for item in addressLabelAllowedValues if item['name'] == address['addressLabel'])['addressLabelID']
                            del address['addressLabel']
                        else:
                            raise TreillageValueError(
                                f"Address label is not valid: {address['addressLabel']}"
                            )
                # if 'addressLabelId' in address.keys():
                    # if address['addressLabelId'] in

                # if metadata and 'addressLabelID' in address.keys() and address['addressLabelID'] in metadata['']:

                addAction('addresses', 'ADD', address)

        # todo: add support for custom fields
        if key.startswith('custom.') and value:
            print("wow, a custom key!")

    return await connection.post(endpoint, body)

""""
body = [{
    'selector': 'firstName',
    'action': 'UPDATE', 'value': 'Mank'}, {'selector': 'middleName', 'action': 'UPDATE', 'value': 'P'}, {'selector': 'lastName', 'action': 'UPDATE', 'value': 'Morkem'}, {'selector': 'nickname', 'action': 'UPDATE', 'value': '#9'}, {'selector': 'prefix', 'action': 'UPDATE', 'value': 'Mr'}, {'selector': 'suffix', 'action': 'UPDATE', 'value': 'Esquire'}, {'selector': 'fromCompany', 'action': 'UPDATE', 'value': 'Vineskills'}, {'selector': 'jobTitle', 'action': 'UPDATE', 'value': 'Optimizer'}, {'selector': 'department', 'action': 'UPDATE', 'value': 'Optimization and Data Management'}, {'selector': 'isDeceased', 'action': 'UPDATE', 'value': True}, {'selector': 'birthdate', 'action': 'UPDATE', 'value': '11/11/1911'}, {'selector': 'deathdate', 'action': 'UPDATE', 'value': '11/11/2019'}, {'selector': 'addresses', 'action': 'ADD', 'value': {'line1': '131 Cool Street', 'line2': 'Apt. 20', 'city': 'Chicago', 'state': 'IL', 'zip': 60623, 'notes': 'The place to Be', 'addressLabelID': 990001441}}, {'selector': 'addresses', 'action': 'ADD', 'value': {'line1': '139 Cool Street', 'line2': 'Apt. 28', 'city': 'Chicago', 'state': 'IL', 'zip': 60631, 'notes': 'The place to Be', 'addressLabelID': 990001442}}]
create_custom_contact(**body)
"""
