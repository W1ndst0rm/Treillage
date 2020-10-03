from typing import List
from .connection_manager import ConnectionManager
from .exceptions import *


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                              Contacts
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


async def get_contact(connection: ConnectionManager, contact_id: str, fields: List[str] = None):
    endpoint = f'/core/contacts/{contact_id}'
    params = dict()
    if fields:
        requested_fields = ','.join(*[fields])
        params['requestedFields'] = requested_fields

    return await connection.get(endpoint, params)


async def get_contact_list(connection: ConnectionManager,
                           fields: List[str] = None,
                           first_name: str = None,
                           last_name: str = None,
                           full_name: str = None,
                           nick_name: str = None,
                           person_type: str = None,
                           phone: str = None,
                           email: str = None
                           ):
    endpoint = '/core/contacts'
    params = dict()
    if fields:
        requested_fields = ','.join(*[fields])
        params['requestedFields'] = requested_fields
    if first_name:
        params['firstName'] = first_name
    if last_name:
        params['lastName'] = last_name
    if full_name:
        params['fullName'] = full_name
    if nick_name:
        params['nickName'] = nick_name
    if person_type:
        params['personType'] = person_type
    if phone:
        params['phone'] = phone
    if email:
        params['email'] = email

    has_more = True
    params['offset'] = 0
    params['limit'] = 50

    while has_more:
        resp = await connection.get(endpoint, params)
        has_more = resp['hasMore']
        params['offset'] += params['limit']
        for contact in resp['items']:
            yield contact


async def create_contact():
    raise NotImplementedError


async def update_contact(connection: ConnectionManager,
                         contact_id: str,
                         person_types: List[str],
                         person_id: dict = None,
                         first_name: str = None,
                         middle_name: str = None,
                         last_name: str = None,
                         is_single_name: bool = None,  # True = Company, False = Individual
                         full_name: str = None,
                         ssn: str = None,  # Displays as "Tax ID" for Companies (i.e. isSingleName = False)
                         birthdate: str = None,
                         notes: str = None,
                         from_company: str = None,
                         specialty: str = None,
                         gender: str = None,  # M = Male, F = Female
                         language: str = None,
                         marital_status: str = None,  # Single Character Values Only Accepted Values:"s","m","d","u","w"
                         is_texting_permitted: bool = None,
                         remarket: bool = None,
                         abbreviated_name: str = None,  # Nickname
                         driver_license_number: str = None,
                         salutation: str = None,
                         bar_number: str = None,
                         fiduciary: str = None,
                         is_minor: bool = None,
                         phones: List = None,
                         emails: List = None,
                         addresses: List = None,
                         ):
    def validate_person_type(person_type) -> bool:
        valid_types = {'Adjuster', 'Attorney', 'Client', 'Court', 'Defendant', 'Plaintiff', 'Expert', 'Firm',
                       'Insurance Company', 'Involved Party', 'Judge', 'Medical Provider'}
        if person_type in valid_types:
            return True
        else:
            raise FilevineValueError(f"{person_type} not in allowed types: {', '.join(*valid_types)}")

    def validate_marital_status(status) -> bool:
        valid_statuses = {"s", "m", "d", "u", "w"}
        if status in valid_statuses:
            return True
        else:
            raise FilevineValueError(f"{status} not in allowed marital statuses of: {', '.join(*valid_statuses)}")

    endpoint = f'/core/contacts/{contact_id}'
    body = dict()
    if person_types:
        body["personTypes"] = []
        for p_type in person_types:
            if validate_person_type(p_type):
                body["personTypes"].append(p_type)
    if person_id:
        if isinstance(person_id, dict):
            body["personId"] = person_id
    if first_name:
        body['firstName'] = first_name
    if middle_name:
        body['middleName'] = middle_name
    if last_name:
        body['lastName'] = last_name
    if is_single_name:
        if isinstance(is_single_name, bool):
            body['isSingleName'] = is_single_name
        else:
            raise FilevineTypeError
    if full_name:
        body['fullName'] = full_name
    if ssn:
        body['ssn'] = ssn
    if birthdate:
        body['birthDate'] = birthdate
    if notes:
        body['notes'] = notes
    if from_company:
        body['fromCompany'] = from_company
    if specialty:
        body["specialty"] = specialty
    if gender:
        body['gender'] = gender
    if language:
        body['language'] = language
    if marital_status:  # Single Character Values Only Accepted Values: "s","m","d","u","w"
        if validate_marital_status(marital_status):
            body['maritalStatus'] = marital_status
    if is_texting_permitted:
        if isinstance(is_texting_permitted, bool):
            body['isTextingPermitted'] = is_texting_permitted
        else:
            raise FilevineTypeError
    if remarket:
        if isinstance(remarket, bool):
            body['remarket'] = remarket
        else:
            raise FilevineTypeError
    if abbreviated_name:
        body['abbreviatedName'] = abbreviated_name
    if driver_license_number:
        body['driverLicenseNumber'] = driver_license_number
    if salutation:
        body['salutation'] = salutation
    if bar_number:
        body['barNumber'] = bar_number
    if fiduciary:
        body['fiduciary'] = fiduciary
    if is_minor:
        body['isMinor'] = is_minor
    if phones:
        if isinstance(phones, List):
            body['phones'] = phones
        else:
            raise FilevineTypeError
    if emails:
        if isinstance(emails, List):
            body['emails'] = emails
        else:
            raise FilevineTypeError
    if addresses:
        if isinstance(addresses, List):
            body['addresses'] = addresses
        else:
            raise FilevineTypeError

    return await connection.patch(endpoint, body)