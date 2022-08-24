import typing
from dataclasses import dataclass
from enum import Enum


class EventTeamStatus:
    """Class representing a team's status during an event.

    Attributes:
        qual (falcon_alliance.EventTeamStatus.Qualifications, optional): Information about the team's rank during qualifications. May be None if qualifications haven't begun yet.
        alliance (falcon_alliance.EventTeamStatus.Alliance, optional): Information about the alliance a team is on, if they are on one. May be None if the team didn't make it onto an alliance.
        playoff (falcon_alliance.EventTeamStatus.Playoff, optional): Playoff status for this team, may be None if the team did not make playoffs, or playoffs have not begun.
        alliance_status_str (str, optional): An HTML formatted string suitable for display to the user containing the team's alliance pick status.
        playoff_status_str (str, optional): An HTML formatter string suitable for display to the user containing the team's playoff status.
        overall_status_str (str, optional): An HTML formatted string suitable for display to the user containing the team's overall status summary of the event.
        next_match_key (str, optional): TBA match key for the next match the team is scheduled to play in at this event, or None.
        last_match_key (str, optional): TBA match key for the last match the team played in at this event, or None.
    """  # noqa

    class Status(Enum):
        """Enum class representing the status of the team during an event.

        Attributes:
            WON (int): Representing if a team won a certain level.
            ELIMINATED (int): Representing if a team was eliminated at a certain level.
            PLAYING (int): Representing if a team is currently playing at that level.
        """

        WON = 1
        ELIMINATED = 2
        PLAYING = 3

    class SortOrders:
        """Information about the team used to determine ranking for an event."""

        def __init__(self, sort_orders: list, sort_order_info: typing.List[dict]):
            self._attributes_formatted = ""

            for data, data_info in zip(sort_orders, sort_order_info):
                snake_case_name = data_info["name"].lower().replace(" ", "_").replace("+", "plus")

                setattr(self, snake_case_name, data)
                self._attributes_formatted += f"{snake_case_name}={data!r}, "

        def __repr__(self):  # pragma: no cover
            return f"SortOrders({self._attributes_formatted.rstrip(', ')})"

    @dataclass()
    class Ranking:
        """Class representing a team's ranking information during qualifications of an event."""

        dq: int
        matches_played: int
        qual_average: typing.Optional[float]
        rank: int
        record: "EventTeamStatus.Record"
        sort_orders: "EventTeamStatus.SortOrders"
        team_key: str

    @dataclass()
    class Alliance:
        """Class representing the alliance said team was on during an event."""

        backup: typing.Optional[dict]
        name: str
        number: int
        pick: int

    @dataclass()
    class Record:
        """Class representing a record of wins, losses and ties for qualification matches, playoffs, and more."""

        losses: int
        ties: int
        wins: int

    @dataclass()
    class Playoff:
        """Class representing the team's performance during playoffs."""

        current_level_record: "EventTeamStatus.Record"
        level: str
        playoff_average: typing.Optional[int]
        record: "EventTeamStatus.Record"
        status: "EventTeamStatus.Status"

    @dataclass()
    class Qualifications:
        """Class representing the team's performance during qualifications."""

        num_teams: int
        ranking: "EventTeamStatus.Ranking"
        status: "EventTeamStatus.Status"

    def __init__(self, event_or_team_key: str, team_status_info: dict):
        self._attributes_formatted = ""

        if event_or_team_key.startswith("frc"):
            self.event_key = None
            self.team_key = event_or_team_key
            self._attributes_formatted += f"{self.team_key=}, "
        else:
            self.team_key = None
            self.event_key = event_or_team_key
            self._attributes_formatted += f"{self.event_key=}, "

        if team_status_info["alliance"]:
            self.alliance = self.Alliance(**team_status_info["alliance"])
        else:
            self.alliance = None

        self._attributes_formatted += "alliance=Alliance(...), "

        self.alliance_status_str = team_status_info["alliance_status_str"]
        self.last_match_key = team_status_info["last_match_key"]
        self.next_match_key = team_status_info["next_match_key"]
        self.overall_status_str = team_status_info["overall_status_str"]

        self._attributes_formatted += (
            f'alliance_status_str="...", {self.last_match_key=}, {self.next_match_key=}, overall_status_str="...", '
        )

        if team_status_info["playoff"]:
            self.playoff = self.Playoff(
                current_level_record=self.Record(**team_status_info["playoff"]["current_level_record"]),
                level=team_status_info["playoff"]["level"],
                playoff_average=team_status_info["playoff"]["playoff_average"],
                record=self.Record(**team_status_info["playoff"]["record"]),
                status=getattr(self.Status, team_status_info["playoff"]["status"].upper()),
            )
        else:
            self.playoff = None

        self.playoff_status_str = team_status_info["playoff_status_str"]
        self._attributes_formatted += 'playoff=Playoff(...), playoff_status_str="...", '

        if team_status_info["qual"]:
            self.qual = self.Qualifications(
                num_teams=team_status_info["qual"]["num_teams"],
                ranking=self.Ranking(
                    dq=team_status_info["qual"]["ranking"]["dq"],
                    matches_played=team_status_info["qual"]["ranking"]["matches_played"],
                    qual_average=team_status_info["qual"]["ranking"]["qual_average"],
                    rank=team_status_info["qual"]["ranking"]["rank"],
                    record=self.Record(
                        **team_status_info["qual"]["ranking"]["record"],
                    ),
                    sort_orders=self.SortOrders(
                        team_status_info["qual"]["ranking"]["sort_orders"], team_status_info["qual"]["sort_order_info"]
                    ),
                    team_key=team_status_info["qual"]["ranking"]["team_key"],
                ),
                status=team_status_info["qual"]["status"],
            )
        else:
            self.qual = None

        self._attributes_formatted += "qual=Qualifications(...)"
        self._attributes_formatted = self._attributes_formatted.replace("self.", "")

    def __repr__(self) -> str:  # pragma: no cover
        return f"EventTeamStatus({self._attributes_formatted})"
