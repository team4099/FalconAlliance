import typing
from dataclasses import dataclass

from .base_schema import BaseSchema

try:
    from utils import *
except ImportError:
    from ..utils import *


class Award(BaseSchema):
    """Class representing an award's information for a team or during an event."""

    @dataclass
    class AwardRecipient:
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
