from typing import List
from .. import ConnectionManager
from .. import TreillageTypeError, TreillageValueError
from ._decorators import get_item, get_item_list, requested_fields


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                              Project Types
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


# GET Project Type
@requested_fields
@get_item
def get_project_type(
    connection: ConnectionManager,
    project_type_id: int,
    requested_fields: List[str] = [""],
):
    return f"/core/projecttypes/{project_type_id}"


# GET Project Type List
@requested_fields
@get_item_list
def get_project_type_list(
    connection: ConnectionManager, requested_fields: List[str] = [""]
):
    return "/core/projecttypes"


# GET Project Type Section
@requested_fields
@get_item
def get_project_type_section(
    connection: ConnectionManager,
    project_type_id: int,
    section_selector: str,
    requested_fields: List[str] = [""],
):
    return f"core/projecttypes/{project_type_id}/sections/{section_selector}"


# GET Project Type Section List
@requested_fields
@get_item_list
def get_project_type_section_list(
    connection: ConnectionManager,
    project_type_id: int,
    requested_fields: List[str] = [""],
):
    return f"core/projecttypes/{project_type_id}/sections"


# GET Project Type Phase List
@requested_fields
@get_item_list
def get_project_type_phase_list(
    connection: ConnectionManager,
    project_type_id: int,
    requested_fields: List[str] = [""],
):
    return f"core/projecttypes/{project_type_id}/phases"
