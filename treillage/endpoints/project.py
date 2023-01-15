from typing import List
from .. import ConnectionManager
from ._decorators import get_item, get_item_list, requested_fields


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                              Projects
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


# GET Project
@requested_fields
@get_item
def get_project(
    connection: ConnectionManager,
    project_id: int,
    requested_fields: List[str] = [""],
):
    return f"/core/project/{project_id}"


# GET Project List
@requested_fields
@get_item_list
def get_project_list(
    connection: ConnectionManager,
    requested_fields: List[str] = [""],
):
    return "/core/projects"


# GET Project Vitals
@requested_fields
@get_item
def get_project_vitals(
    connection: ConnectionManager,
    project_id: int,
    requested_fields: List[str] = [""],
):
    return f"/core/projects/{project_id}/vitals"
