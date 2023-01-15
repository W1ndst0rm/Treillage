from typing import List, Dict
from .. import TreillageValidationError


class Contact:
    def __init__(
        self,
        firstName: str,
        middleName: str = "",
        lastName: str = "",
        nickname: str = "",
        prefix: str = "",
        suffix: str = "",
        fromCompany: str = "",
        jobTitle: str = "",
        department: str = "",
        isSingleName: bool = True,
        isArchived: bool = False,
        isDeceased: bool = False,
        birthdate: str = "",
        deathdate: str = "",
        addresses: List[dict] = [],
        phones: List[dict] = [],
        emails: List[dict] = [],
        personTypes: List[str] = [],
        hashtags: List[str] = [],
        customFields: dict = {},
        metadata: List[dict] = [],
    ):
        self.firstName = firstName
        self.middleName = middleName
        self.lastName = lastName
        self.nickname = nickname
        self.prefix = prefix
        self.suffix = suffix
        self.fromCompany = fromCompany
        self.jobTitle = jobTitle
        self.department = department
        self.isSingleName = isSingleName
        self.isArchived = isArchived
        self.isDeceased = isDeceased
        self.birthdate = birthdate
        self.deathdate = deathdate
        self.addresses = addresses
        self.phones = phones
        self.emails = emails
        self.personTypes = personTypes
        self.addresses = addresses
        self.hashtags = hashtags
        self.customFields = customFields
        self.metadata = metadata

    def build_body_custom(self):
        arguments = [x for x in vars(self).items()]

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

                if self.metadata:
                    if key == "addresses":
                        mode = "address"
                    if key == "phones":
                        mode = "phone"
                    if key == "emails":
                        mode = "email"

                    labelAllowedValues = next(
                        item for item in self.metadata if item["selector"] == key
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
                        if item[f"{mode}Label"] in [
                            x["name"] for x in labelAllowedValues
                        ]:
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
        for key, value in arguments:

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

            if self.metadata:
                if key == "personTypes" and value:
                    personTypes = value.split(", ")
                    allowedTypes = next(
                        item for item in self.metadata if item["selector"] == key
                    )["allowedValues"]
                    for personType in personTypes:
                        try:
                            id = next(
                                x for x in allowedTypes if x["name"] == personType
                            )["value"]
                        except:
                            raise TreillageValidationError(
                                f"Invalid personType: {personType}"
                            )
                        addAction(key, "ADD", id)

                if key.startswith("custom."):
                    try:
                        field = next(x for x in self.metadata if x["selector"] == key)
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
        return body
