from .identifier import Identifier
from typing import Union


class Project:
    def __init__(
        self,
        clientId: Union[Identifier, int],
        projectTypeId: Union[Identifier, int],
        projectName: str,
        clientPartnerId: str = "",
        projectTypePartnerId: str = "",
        incident_date: str = "",
        description: str = "",
    ):
        if type(clientId) == Identifier:
            self.clientId = clientId
        elif type(clientId) == int:
            self.clientId = Identifier(native=clientId, partner=clientPartnerId)

        if type(projectTypeId) == Identifier:
            self.projectTypeId = projectTypeId
        else:
            self.projectTypeId = Identifier(
                native=projectTypeId, partner=projectTypePartnerId
            )
        self.projectName = projectName
        self.incidentDate = incident_date
        self.description = description

    def __repr__(self) -> str:
        return self.projectName
