import typing

from .base_schema import BaseSchema


class Robot(BaseSchema):
    """Class representing a robot containing methods to get specific district information.

    Attributes:
        year (int, optional): Year this robot competed in.
        robot_name (str, optional): Name of the robot as provided by the team.
        key (str): Internal TBA identifier for this robot.
        team_key (str, optional): TBA team key for this robot.
    """

    def __init__(self, **kwargs):
        self.year: typing.Optional[int] = kwargs.get("year")
        self.robot_name: typing.Optional[str] = kwargs.get("robot_name")
        self.key: str = kwargs["key"]
        self.team_key: typing.Optional[str] = kwargs.get("team_key")

        super().__init__()
