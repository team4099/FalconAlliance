import datetime
import typing
from dataclasses import dataclass

from .base_schema import BaseSchema

try:
    from falcon_alliance_utils import *  # noqa
except ImportError:
    from ..falcon_alliance_utils import *  # noqa


class Match(BaseSchema):
    """Class representing a match's metadata with methods to get match specific data.

    Attributes:
        key (str): TBA match key with the format yyyy[EVENT_CODE]_[COMP_LEVEL]m[MATCH_NUMBER], where yyyy is the year, and EVENT_CODE is the event code of the event, COMP_LEVEL is (qm, ef, qf, sf, f), and MATCH_NUMBER is the match number in the competition level. A set number may be appended to the competition level if more than one match in required per set.
        comp_level (str, optional): The competition level the match was played at.
        set_number (int, optional): The set number in a series of matches where more than one match is required in the match series.
        match_number (int, optional): The match number of the match in the competition level.
        alliances (list[falcon_alliance.Match.Alliance], optional): A list of alliances, the teams on the alliances, and their score.
        winning_alliance (str, optional): The color (red/blue) of the winning alliance. Will contain an empty string in the event of no winner, or a tie.
        event_key (str, optional): Event key of the event the match was played at.
        time (datetime.datetime, optional): UNIX timestamp (seconds since 1-Jan-1970 00:00:00) of the scheduled match time, as taken from the published schedule.
        actual_time (datetime.datetime, optional): UNIX timestamp (seconds since 1-Jan-1970 00:00:00) of actual match start time.
        predicted_time (datetime.datetime, optional): UNIX timestamp (seconds since 1-Jan-1970 00:00:00) of the TBA predicted match start time.
        post_result_time (datetime.datetime, optional): UNIX timestamp (seconds since 1-Jan-1970 00:00:00) when the match result was posted.
        score_breakdown (dict, optional): Score breakdown for auto, teleop, etc. points. Varies from year to year. May be None.
        videos (list, optional): A list of video objects associated with this match.
    """  # noqa

    @dataclass()
    class Alliance:
        """Class representing an alliance's performance/metadata during a match."""

        color: typing.Union[typing.Literal["blue"], typing.Literal["red"]]
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
            "red": self.Alliance(**alliances["red"], color="red"),
            "blue": self.Alliance(**alliances["blue"], color="blue"),
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

    def alliance_of(self, team_key: typing.Union[int, str, "Team"]) -> typing.Optional[Alliance]:
        """
        Returns the alliance of the team provided, can return None if a team is in neither of the alliances for a match.

        Args:
            team_key (int, str, falcon_alliance.Team): An integer representing the team number to search for in the alliance team keys or a string representing the team key to search for in the alliance team keys or a Team object representing the team to get the alliance of.
        """  # noqa
        team_key = to_team_key(team_key)

        if team_key in (
            *self.alliances["red"].team_keys,
            *self.alliances["red"].surrogate_team_keys,
            *self.alliances["red"].dq_team_keys,
        ):
            return self.alliances["red"]
        elif team_key in (
            *self.alliances["blue"].team_keys,
            *self.alliances["blue"].surrogate_team_keys,
            *self.alliances["blue"].dq_team_keys,
        ):
            return self.alliances["blue"]
