from typing import List, Dict
from .. import ConnectionManager
from .. import TreillageValidationError
from .list_paginator import list_paginator
import json


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                             Custom Contacts
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


async def get_contact_metadata(connection: ConnectionManager, fields: List[str] = None):
    endpoint = f"/core/custom-contacts-meta"
    params = dict()
    if fields:
        requested_fields = ",".join(*[fields])
        params["requestedFields"] = requested_fields
    return await connection.get(endpoint, params)


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
    phones: List[dict] = None,
    emails: List[dict] = None,
    personTypes: List[str] = None,
    metadata: List[dict] = None,  # can this be cached instead of passing as arg?
    **kwargs,
):

    arguments = locals().copy()
    for arg, val in kwargs.items():
        arguments[arg] = val
    endpoint = f"/core/custom-contacts/"

    body = list()

    def addAction(key, action, value):
        body.append({"selector": key, "action": action, "value": value})

    standardStringFields = "firstName middleName lastName nickname prefix suffix fromCompany jobTitle department birthdate deathdate".split()
    standardBoolFields = "isSingleName isArchived isDeceased".split()
    addressFields = (
        "line1 line2 city state zip notes addressLabel addressLabelID".split()
    )
    phoneFields = "number notes phoneLabel phoneLabelID".split()
    emailFields = "address notes emailLabel emailLabelId".split()

    def processAddressEmailPhone(key, value, fields):
        if not isinstance(value, List):
            raise TreillageValidationError(f"{key} must be a list.")

        for item in value:

            if not isinstance(item, Dict):
                raise TreillageValidationError(
                    f"'{key}' must be a list of dictionaries"
                )

            if not set(item.keys()).issubset(fields):
                raise TreillageValidationError(
                    f"{key} includes invalid fields:" + f"{item.keys()}"
                )

            if item.get("state"):
                if len(item["state"]) > 2:
                    raise TreillageValidationError(
                        f"State field cannot be > 2 characters: " + item["state"]
                    )

            if metadata:
                if key == "addresses":
                    mode = "address"
                if key == "phones":
                    mode = "phone"
                if key == "emails":
                    mode = "email"

                labelAllowedValues = next(
                    item for item in metadata if item["selector"] == key
                )["allowedValues"]

                # validate LabelID
                if item.get(f"{mode}LabelID"):
                    if not item[f"{mode}LabelID"] in [
                        x[f"{mode}]LabelID"] for x in labelAllowedValues
                    ]:
                        raise TreillageValidationError(
                            f"{mode}LabelID is not valid: {item[f'{mode}LabelID']}"
                        )
                # Replace label with labelID
                if item.get(f"{mode}Label"):
                    if item[f"{mode}Label"] in [x["name"] for x in labelAllowedValues]:
                        item[f"{mode}LabelID"] = next(
                            x
                            for x in labelAllowedValues
                            if x["name"] == item[f"{mode}Label"]
                        )[f"{mode}LabelID"]
                        del item[f"{mode}Label"]
                    else:
                        invalidLabel = item[f"{mode}Label"]
                        raise TreillageValidationError(
                            f"{mode} label is not valid: {invalidLabel}"
                        )
            # if address/phone/email passed validation, add it to the body
            addAction(key, "ADD", item)

    # Begin processing arguments:
    for key, value in arguments.items():

        if key in standardStringFields and value:
            addAction(key, "UPDATE", value)

        if key in standardBoolFields:
            if isinstance(value, bool):
                addAction(key, "UPDATE", value)
            else:
                raise TreillageValidationError(f"{key}: {value} is not a bool")

        if key == "hashtags" and value:
            try:
                tags = value.split(", ")
                for tag in tags:
                    addAction("hashtags", "ADD", tag)
            except:
                raise TreillageValidationError(f"Invalid hashtags: {value}")

        if key == "addresses" and value:
            processAddressEmailPhone(key, value, addressFields)

        if key == "phones" and value:
            processAddressEmailPhone(key, value, phoneFields)

        if key == "emails" and value:
            processAddressEmailPhone(key, value, emailFields)

        if metadata:
            if key == "personTypes" and value:
                personTypes = value.split(", ")
                allowedTypes = next(
                    item for item in metadata if item["selector"] == key
                )["allowedValues"]
                for personType in personTypes:
                    try:
                        id = next(x for x in allowedTypes if x["name"] == personType)[
                            "value"
                        ]
                    except:
                        raise TreillageValidationError(
                            f"Invalid personType: {personType}"
                        )
                    addAction(key, "ADD", id)

            if key.startswith("custom.") and value is not None:
                try:
                    field = next(x for x in metadata if x["selector"] == key)
                    action = next(
                        iter(
                            field["action"].split("|")
                        )  # "action": "UPDATE|REMOVE" / "actions": "ADD|REMOVE"
                    )
                    if field.get("allowedValues"):
                        allowedValues = field["allowedValues"]
                        if value not in allowedValues:
                            raise TreillageValidationError(
                                f"{value} is an invalid value for {key}. Allowed values are {allowedValues}"
                            )
                    addAction(key, action, value)
                except:
                    raise TreillageValidationError(
                        f"Invalid custom field: {key}={value}"
                    )

    return await connection.post(endpoint, body)
