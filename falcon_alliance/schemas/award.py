import typing
from dataclasses import dataclass

from falcon_alliance.schemas.base_schema import BaseSchema

try:
    from falcon_alliance_utils import *
except ImportError:
    from ..utils import *


class Award(BaseSchema):
    """Class representing an award's information for a team or during an event.

    Attributes:
        name (str): The name of the award as provided by FIRST. May vary for the same award type.
        award_type (int): Type of award given. See https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/award_type.py#L6
        event_key (str): The event_key of the event the award was won at.
        recipient_list (list[falcon_alliance.Award.AwardRecipient): A list of recipients of the award at the event. May have either a team_key or an awardee, both, or neither (in the case the award wasn't awarded at the event).
        year (int): The year this award was won.
    """  # noqa

    @dataclass
    class AwardRecipient:
        """Class containing information about an award's recipient."""

        team_key: str
        awardee: typing.Optional[str]

    def __init__(self, **kwargs):
        self.name: typing.Optional[str] = kwargs.get("name")
        self.award_type: typing.Optional[int] = kwargs.get("award_type")
        self.event_key: typing.Optional[str] = kwargs.get("event_key")
        self.recipient_list: typing.Optional[list] = [
            self.AwardRecipient(**recipient_data) for recipient_data in kwargs.get("recipient_list", [])
        ]
        self.year: typing.Optional[int] = kwargs.get("year")

        super().__init__()
