import datetime
import typing
from dataclasses import dataclass

from .base_schema import BaseSchema

try:
    from utils import *  # noqa
except ImportError:
    from ..utils import *  # noqa


class Match(BaseSchema):
    """Class representing a match's metadata with methods to get match specific data."""

    @dataclass()
    class Alliance:
        """Class representing an alliance's performance/metadata during a match."""

        score: typing.Optional[int]
        team_keys: typing.List[str]
        surrogate_team_keys: typing.List[str]
        dq_team_keys: typing.List[str]

    @dataclass()
    class ZebraMotionworks:
        """Class representing Zebra MotionWorks data for a team during a match."""

        key: str
        times: typing.List[float]
        alliances: "Team"

        @dataclass()
        class Team:
            """Class representing a team's specific Zebra MotionWorks data during a match."""

            team_key: str
            xs: list
            ys: list

        def __post_init__(self):
            self.alliances = {
                "red": [self.Team(**team) for team in self.alliances["red"]],
                "blue": [self.Team(**team) for team in self.alliances["blue"]],
            }

    def __init__(self, **kwargs):
        self.key: str = kwargs["key"]

        self.comp_level: typing.Optional[str] = kwargs.get("comp_level")
        self.set_number: typing.Optional[int] = kwargs.get("set_number")

        self.match_number: typing.Optional[int] = kwargs.get("match_number")

        alliances = kwargs.get("alliances")
        self.alliances: typing.Optional[dict] = {
            "red": self.Alliance(**alliances["red"]),
            "blue": self.Alliance(**alliances["blue"]),
        }
        self.winning_alliance: typing.Optional[str] = kwargs.get("winning_alliance")

        self.event_key: typing.Optional[str] = kwargs.get("event_key")

        time = kwargs.get("time")
        actual_time = kwargs.get("actual_time")
        predicted_time = kwargs.get("predicted_time")
        post_result_time = kwargs.get("post_result_time")

        self.time: typing.Optional[datetime.datetime] = datetime.datetime.fromtimestamp(time) if time else None
        self.actual_time: typing.Optional[int] = datetime.datetime.fromtimestamp(actual_time) if actual_time else None
        self.predicted_time: typing.Optional[int] = (
            datetime.datetime.fromtimestamp(predicted_time) if predicted_time else None
        )
        self.post_result_time: typing.Optional[int] = (
            datetime.datetime.fromtimestamp(post_result_time) if post_result_time else None
        )

        self.score_breakdown: typing.Optional[dict] = kwargs.get("score_breakdown")
        self.videos: typing.Optional[list] = kwargs.get("videos")

        super().__init__()
