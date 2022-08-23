import asyncio
import datetime
import functools
import itertools
import typing
from dataclasses import dataclass
from re import match
from statistics import mean

from .award import Award
from .base_schema import BaseSchema
from .event_team_status import EventTeamStatus
from .match import Match
from .media import Media
from .robot import Robot

try:
    from utils import *
except ImportError:
    from ..utils import *

__all__ = ["District", "Event", "Team"]
PARSING_FORMAT = "%Y-%m-%d"


class District(BaseSchema):
    """Class representing a district containing methods to get specific district information."""

    @dataclass()
    class Ranking:
        """Class representing a team's ranking in a given district."""

        team_key: str
        rank: int
        rookie_bonus: int
        other_bonus: typing.Optional[int] = None
        point_total: int = 0
        event_points: typing.List[dict] = None

    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            if isinstance(args[0], int) and isinstance(args[1], str):
                self.abbreviation = args[1]
                self.year = args[0]
                self.key = f"{self.year}{self.abbreviation}"
            elif isinstance(args[0], str) and isinstance(args[1], int):
                self.abbreviation = args[0]
                self.year = args[1]
                self.key = f"{self.year}{self.abbreviation}"
        elif len(args) == 1:
            (self.key,) = args
            self.year: typing.Optional[int] = kwargs.get("year") or int(match(r"\d+", self.key)[0])
            self.abbreviation: typing.Optional[str] = kwargs.get("abbreviation") or self.key.replace(str(self.year), "")
        else:
            self.key: str = kwargs["key"]
            self.year: typing.Optional[int] = kwargs.get("year") or int(match(r"\d+", self.key)[0])
            self.abbreviation: typing.Optional[str] = kwargs.get("abbreviation") or self.key.replace(str(self.year), "")

        self.display_name: typing.Optional[str] = kwargs.get("display_name")

        super().__init__()

    def events(
        self,
        simple: bool = False,
        keys: bool = False,
    ) -> typing.List[typing.Union[str, "Event"]]:
        """
        Retrieves a list of events in the given district.

        Args:
            simple (bool): A boolean that specifies whether the results for each event should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the keys of the events in a given district should be retrieved.

        Returns:
            - list[str]: A list of strings with each string representing an event's key for all the events in the given district
            - list[Event]: A list of Event objects with each object representing an event in the given district.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url("district", key=self.key, endpoint="events", simple=simple, keys=keys),
                headers=self._headers,
            )
        )
        if keys:
            return response
        else:
            return [Event(**event_data) for event_data in response]

    def teams(
        self,
        simple: bool = False,
        keys: bool = False,
    ) -> typing.List[typing.Union[str, "Team"]]:
        """
        Retrieves a list of teams in the given district.

        Parameters:
            simple:
                A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys:
                A boolean that specifies whether only the keys of the teams in a given district should be retrieved.

        Returns:
            A list of strings with each string representing a team's key for all the teams in the given district or a list of Team objects with each object representing a team in the given district.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url("district", key=self.key, endpoint="teams", simple=simple, keys=keys),
                headers=self._headers,
            )
        )
        if keys:
            return response
        else:
            return [Team(**event_data) for event_data in response]

    def rankings(self) -> typing.List[Ranking]:
        """
        Retrieves a list of team district rankings for the given district.

        Returns:
            A list of Ranking objects with each Ranking object representing a team's district ranking for the given district.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("district", key=self.key, endpoint="rankings"), headers=self._headers)
        )
        return [self.Ranking(**team_ranking_data) for team_ranking_data in response]


class Event(BaseSchema):
    """Class representing an event containing methods to get specific event information."""

    @dataclass()
    class DistrictPoints:
        """Class representing an event's district points given for all teams."""

        points: typing.Dict[str, typing.Dict[str, int]]
        tiebreakers: typing.Dict[str, typing.Dict[str, int]]

    @dataclass()
    class Status:
        """Class representing a status of an alliance during an event."""

        playoff_average: float
        level: str
        record: "Event.Record"
        current_level_record: "Event.Record"
        status: str

    @dataclass()
    class Record:
        """Class representing a record of wins, losses and ties for either a certain level or throughout the event."""

        losses: int
        ties: int
        wins: int

    class Alliance(BaseSchema):
        """Class representing an alliance in an event."""

        def __init__(
            self,
            name: str,
            declines: typing.List[str],
            picks: typing.List[str],
            status: dict,
            backup: typing.Optional[dict] = None,
        ):
            self.name = name
            self.backup = backup
            self.declines = declines
            self.picks = picks
            self.status: Event.Status = Event.Status(
                playoff_average=status["playoff_average"],
                level=status["level"],
                record=Event.Record(**status["record"]),
                current_level_record=Event.Record(**status["current_level_record"]),
                status=status["status"],
            )

            super().__init__()

    @dataclass()
    class Insights:
        """Class representing the insights of an event (specific by year)"""

        qual: dict
        playoff: dict

    @dataclass()
    class OPRs:
        """Class representing different metrics (OPR/DPR/CCWMs) for teams during an event."""

        oprs: dict
        dprs: dict
        ccwms: dict

        def average(self, metric: typing.Optional[str] = None) -> typing.Union[dict, float]:
            """
            Gets the average of all the metrics for said event; could also only get one average for a specific metric if you aren't interested in all metrics.

            Parameters:
                metric:
                    A string representing which metric to get the average for (opr/dpr/ccwm). `metric` is optional, and if not passed in, the averages for all metrics will be retrieved.

            Returns:
                A dictionary containing the averages for all metrics or a decimal (float object) representing the average of one of the metrics if specified.
            """  # noqa
            metric_data_mapping = {"opr": self.oprs, "dpr": self.dprs, "ccwm": self.ccwms}

            if metric:
                if metric.lower() not in metric_data_mapping.keys():
                    raise ValueError("metric must be either 'opr', 'dpr', or 'ccwm'")

                metric_data = metric_data_mapping[metric.lower()]

                return mean(metric_data.values())
            else:
                return {
                    "opr": mean(self.oprs.values()),
                    "dpr": mean(self.dprs.values()),
                    "ccwm": mean(self.ccwms.values()),
                }

    class ExtraStats:
        """Information about extra statistics regarding the ranking of a team during an event."""

        def __init__(self, extra_stats: list, extra_stats_info: typing.List[dict]):
            self._attributes_formatted = ""

            for data, data_info in zip(extra_stats, extra_stats_info):
                snake_case_name = data_info["name"].lower().replace(" ", "_").replace("+", "plus")

                setattr(self, snake_case_name, data)
                self._attributes_formatted += f"{snake_case_name}={data!r}, "

        def __repr__(self):  # pragma: no cover
            return f"ExtraStats({self._attributes_formatted.rstrip(', ')})"

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
        """Class representing a team's ranking during an event."""

        dq: int
        extra_stats: "Event.ExtraStats"
        matches_played: int
        qual_average: int
        rank: int
        record: "Event.Record"
        sort_orders: "Event.SortOrders"
        team_key: str

    @dataclass()
    class Webcast:
        """Class representing metadata and information about a webcast for an event."""

        type: str
        channel: str
        date: typing.Optional[str] = None
        file: typing.Optional[str] = None

        def __post_init__(self):
            if self.date:
                self.date: datetime.datetime = datetime.datetime.strptime(self.date, PARSING_FORMAT)

    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            self.year = int(args[0])
            self.event_code = args[1]
            self.key = f"{args[0]}{args[1]}"
        elif len(args) == 1:
            (self.key,) = args
            self.year: int = kwargs.get("year") or int(match(r"\d+", self.key)[0])
            self.event_code: str = kwargs.get("event_code") or self.key.replace(str(self.year), "")
        else:
            self.key: str = kwargs["key"]
            self.year: int = kwargs.get("year") or int(match(r"\d+", self.key)[0])
            self.event_code: str = kwargs.get("event_code") or self.key.replace(str(self.year), "")

        self.name: typing.Optional[str] = kwargs.get("name")
        self.event_type: typing.Optional[int] = kwargs.get("event_type")

        district_data = kwargs.get("district")
        self.district: typing.Optional[dict] = District(**district_data) if district_data else None

        self.city: typing.Optional[str] = kwargs.get("city")
        self.state_prov: typing.Optional[str] = kwargs.get("state_prov")
        self.country: typing.Optional[str] = kwargs.get("country")

        try:
            self.start_date: typing.Optional[datetime.datetime] = datetime.datetime.strptime(
                kwargs["start_date"], PARSING_FORMAT
            )
            self.end_date: typing.Optional[datetime.datetime] = datetime.datetime.strptime(
                kwargs["end_date"], PARSING_FORMAT
            )
        except KeyError:
            self.start_date = None
            self.end_date = None

        self.short_name: typing.Optional[str] = kwargs.get("short_name")
        self.event_type_string: typing.Optional[str] = kwargs.get("event_type_string")
        self.week: typing.Optional[int] = kwargs.get("week")

        self.address: typing.Optional[str] = kwargs.get("address")
        self.postal_code: typing.Optional[str] = kwargs.get("postal_code")
        self.gmaps_place_id: typing.Optional[str] = kwargs.get("gmaps_place_id")
        self.gmaps_url: typing.Optional[str] = kwargs.get("gmaps_url")
        self.lat: typing.Optional[float] = kwargs.get("lat")
        self.lng: typing.Optional[float] = kwargs.get("lng")
        self.location_name: typing.Optional[str] = kwargs.get("location_name")
        self.timezone: typing.Optional[str] = kwargs.get("timezone")

        self.website: typing.Optional[str] = kwargs.get("website")

        self.first_event_id: typing.Optional[str] = kwargs.get("first_event_id")
        self.first_event_code: typing.Optional[str] = kwargs.get("first_event_code")

        self.webcasts: typing.Optional[list] = [
            self.Webcast(**webcast_data) for webcast_data in kwargs.get("webcasts", []) if webcast_data
        ]

        self.division_keys: typing.Optional[list] = kwargs.get("division_keys")
        self.parent_event_key: typing.Optional[str] = kwargs.get("parent_event_key")

        self.playoff_type: typing.Optional[int] = kwargs.get("playoff_type")
        self.playoff_type_string: typing.Optional[str] = kwargs.get("playoff_type_string")

        super().__init__()

    def alliances(self) -> typing.List[Alliance]:
        """
        Retrieves all alliances of an event.

        Returns:
            A list of Alliance objects representing each alliance in the event.
        """
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("event", key=self.key, endpoint="alliances"), headers=self._headers)
        )
        return [self.Alliance(**alliance_info) for alliance_info in response]

    def awards(self) -> typing.List[Award]:
        """
        Retrieves all awards distributed in an event.

        Returns:
            A list of Award objects representing each award distributed in an event.
        """
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("event", key=self.key, endpoint="awards"), headers=self._headers)
        )
        return [Award(**award_info) for award_info in response]

    def district_points(self) -> typing.Optional[DistrictPoints]:
        """
        Retrieves district points for teams during an event for both qualification and tiebreaker matches.

        Returns:
            A DistrictPoints object containing "points" and "tiebreakers" fields, with each field possessing a dictionary mapping team keys to their points or None if the event doesn't take place in a district or district points are not applicable to the event.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url("event", key=self.key, endpoint="district_points"), headers=self._headers
            )
        )

        if response:
            return self.DistrictPoints(**response)

    def insights(self) -> typing.Optional[Insights]:
        """
        Retrieves insights of an event (specific data about performance and the like at the event; specific by game).
        Insights can only be retrieved for any events from 2016 and onwards.

        Returns:
            An Insight object containing qualification and playoff insights from the event. Can be None if the event hasn't occurred yet, and the fields of Insight may be None depending on how far the event has advanced.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("event", key=self.key, endpoint="insights"), headers=self._headers)
        )

        if response:
            return self.Insights(**response)

    def matches(
        self, simple: bool = False, keys: bool = False, timeseries: bool = False
    ) -> typing.List[typing.Union[str, Match]]:
        """
        Retrieves all matches that occurred during an event.

        Per TBA, the timeseries data is in development and therefore you should NOT rely on it.

        Parameters:
            simple:
                A boolean that specifies whether the results for each match should be 'shortened' and only contain more relevant information.
            keys:
                A boolean that specifies whether only the keys of the matches should be retrieved.
            timeseries:
                A boolean that specifies whether only the keys of the matches that have timeseries data should be retrieved.

        Returns:
            A dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary or a list of strings representing the keys of the teams that participated in an event or a list of Team objects, each representing a team that participated in an event.
        """  # noqa
        if (simple, keys, timeseries).count(True) > 1:
            raise ValueError(
                "Only one parameter out of `simple`, `keys`, and `statuses`"
                " can be True. You can't mix and match parameters."
            )

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url(
                    "event", key=self.key, endpoint="matches", simple=simple, keys=keys, timeseries=timeseries
                ),
                headers=self._headers,
            )
        )
        if keys or timeseries:
            return response
        else:
            return [Match(**match_data) for match_data in response]

    def oprs(self) -> OPRs:
        """
        Retrieves different metrics for all teams during an event.
        To see an explanation on OPR and other metrics retrieved from an event, see https://www.thebluealliance.com/opr.

        Returns:
            An OPRs object containing a key/value pair for the OPRs, DPRs, and CCWMs of all teams at an event. The fields of `OPRs` may be empty if OPRs, DPRs, and CCWMs weren't calculated.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("event", key=self.key, endpoint="oprs"), headers=self._headers)
        )

        if response:
            return self.OPRs(**response)
        else:  # pragma: no cover
            return self.OPRs(oprs={}, dprs={}, ccwms={})

    def predictions(self) -> dict:
        """
        Retrieves predictions for matches of an event. May not work for all events since this endpoint is in beta per TBA.

        Returns:
            A dictionary containing the predictions of an event from TBA (contains year-specific information). May be an empty dictionary if there are no predictions available for that event.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("event", key=self.key, endpoint="predictions"), headers=self._headers)
        )
        return response

    def rankings(self) -> typing.Dict[str, Ranking]:
        """
        Retrieves a list of team rankings for an event.

        Returns:
            A dictionary with team keys as the keys of the dictionary and Ranking objects for that team's information about their ranking at an event as values of the dictionary.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("event", key=self.key, endpoint="rankings"), headers=self._headers)
        )
        rankings_dict = {}

        for rank_info in response["rankings"]:
            rank_info["extra_stats"] = self.ExtraStats(rank_info["extra_stats"], response["extra_stats_info"])
            rank_info["sort_orders"] = self.SortOrders(rank_info["sort_orders"], response["sort_order_info"])

            rankings_dict[rank_info["team_key"]] = self.Ranking(**rank_info)

        return rankings_dict

    def teams(
        self, simple: bool = False, keys: bool = False, statuses: bool = False
    ) -> typing.Union[typing.List[typing.Union[str, "Team"]], typing.Dict[str, EventTeamStatus]]:
        """
        Retrieves all teams who participated at an event.

        Parameters:
            simple:
                A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys:
                A boolean that specifies whether only the names of the FRC teams should be retrieved.
            statuses:
                A boolean that specifies whether a key/value pair of the statuses of teams in an event should be returned.

        Returns:
            A dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary or a list of strings representing the keys of the teams that participated in an event or a list of Team objects, each representing a team that participated in an event.
        """  # noqa
        if (simple, keys, statuses).count(True) > 1:
            raise ValueError(
                "Only one parameter out of `simple`, `keys`, and `statuses` can be True."
                " You can't mix and match parameters."
            )

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url("event", key=self.key, endpoint="teams", simple=simple, keys=keys, statuses=statuses),
                headers=self._headers,
            )
        )
        if keys:
            return response
        elif statuses:
            return {
                team_key: EventTeamStatus(team_key, team_status_info)
                for team_key, team_status_info in response.items()
                if team_status_info
            }
        else:
            return [Team(**team_data) for team_data in response]


class Team(BaseSchema):
    """Class representing a team's metadata with methods to get team specific data."""

    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            if isinstance(args[0], int) and isinstance(args[1], str):
                self.key = f"{args[1]}{args[0]}"
                self.team_number = args[0]
            elif isinstance(args[0], str) and isinstance(args[1], int):
                self.key = f"{args[0]}{args[1]}"
                self.team_number = args[1]
        elif len(args) == 1:
            if isinstance(args[0], int):
                self.key = f"frc{args[0]}"
            else:
                (self.key,) = args
            self.team_number: int = int(self.key[3:])
        else:
            self.key: str = kwargs["key"]
            self.team_number: int = kwargs.get("team_number") or int(self.key[3:])

        self.nickname: typing.Optional[str] = kwargs.get("nickname")
        self.name: typing.Optional[int] = kwargs.get("name")
        self.school_name: typing.Optional[str] = kwargs.get("school_name")
        self.city: typing.Optional[str] = kwargs.get("city")
        self.state_prov: typing.Optional[str] = kwargs.get("state_prov")
        self.country: typing.Optional[str] = kwargs.get("country")
        self.address: typing.Optional[str] = kwargs.get("address")
        self.postal_code: typing.Optional[int] = kwargs.get("postal_code")
        self.gmaps_place_id: typing.Optional[str] = kwargs.get("gmaps_place_id")
        self.gmaps_url: typing.Optional[str] = kwargs.get("gmaps_url")
        self.lat: typing.Optional[float] = kwargs.get("lat")
        self.lng: typing.Optional[float] = kwargs.get("lng")
        self.location_name: typing.Optional[float] = kwargs.get("location_name")
        self.rookie_year: typing.Optional[int] = kwargs.get("rookie_year")
        self.home_championship: typing.Optional[dict] = kwargs.get("home_championship")

        super().__init__()

    async def _get_year_events(
        self, year: int, simple: bool, keys: bool, statuses: bool
    ) -> typing.Union[typing.List[typing.Union[str, Event]], typing.Dict[str, EventTeamStatus]]:
        """
        Retrieves and returns all events from a year based on the parameters given.

        Parameters:
            year:
                An integer that specifies if only the events the team participated from that year should be retrieved.
            simple:
                A boolean that specifies whether the results for each event should be 'shortened' and only contain more relevant information.
            keys:
                A boolean that specifies whether only the names of the events this team has participated in should be returned.
            statuses:
                A boolean that specifies whether a key/value pair of the statuses of teams in an event should be returned.

        Returns:
            A list of Event objects for each event that was returned or a list of strings representing the keys of the events or a dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary.
        """  # noqa
        response = await InternalData.get(
            url=construct_url(
                "team", key=self.key, endpoint="events", year=year, simple=simple, keys=keys, statuses=statuses
            ),
            headers=self._headers,
        )
        if keys:
            return response
        elif not statuses:
            return [Event(**event_data) for event_data in response]
        else:
            return {
                event_key: EventTeamStatus(event_key, team_status_info)
                for event_key, team_status_info in response.items()
                if team_status_info
            }

    async def _get_year_matches(
        self, year: int, event_code: typing.Optional[str], simple: bool, keys: bool
    ) -> typing.List[Match]:
        """
        Retrieves all matches a team played from a certain year.

        Parameters:
            year:
                An integer representing the year to retrieve a team's matches from.
            event_code:
                A string representing the code of an event (the latter half of a key, eg 'iri' instead of '2022iri'). Used for filtering matches a team played to only those in a certain event.
            simple:
                A boolean representing whether each match's information should be stripped to only contain relevant information.
            keys:
                A boolean representing whether only the keys of the matches a team played from said year should be returned:

        Returns:
            A list of Match objects representing each match a team played based on the conditions; might be empty if team didn't play matches that year.
        """  # noqa
        response = await InternalData.get(
            url=construct_url("team", key=self.key, endpoint="matches", year=year, simple=simple, keys=keys),
            headers=self._headers,
        )
        if keys:
            if event_code:
                return [match_key for match_key in response if event_code in match_key]
            else:
                return response
        else:
            if event_code:
                return [Match(**match_data) for match_data in response if event_code in match_data["event_key"]]
            else:
                return [Match(**match_data) for match_data in response]

    async def _get_year_media(self, year: int, media_tag: typing.Optional[str] = None) -> typing.List[Media]:
        """
        Retrieves all the media of a certain team from a certain year and based off the media_tag if passed in.

        Parameters:
            year:
                An integer representing a year to retrieve a team's media from.
            media_tag:
                A string representing the type of media to be returned. Can be None if media_tag is not passed in.

        Returns:
            A list of Media objects representing individual media from a team during a year.
        """
        if media_tag:
            url = construct_url(
                "team", key=self.key, endpoint="media", second_endpoint="tag", media_tag=media_tag, year=year
            )
        else:
            url = construct_url("team", key=self.key, endpoint="media", year=year)

        response = await InternalData.get(url=url, headers=self._headers)
        return [Media(**media_data) for media_data in response]

    def awards(self, year: typing.Optional[typing.Union[range, int]] = None) -> typing.List[Award]:
        """
        Retrieves all awards a team has gotten either during its career or during certain year(s).

        Parameters:
            year:
                An integer representing a year that the awards should be returned for or a range object representing the years that awards should be returned from. Can be None if no year is passed in as it is an optional parameter.

        Returns:
            A list of Award objects representing each award a team has got based on the parameters; may be empty if the team has gotten no awards.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url(
                    "team", key=self.key, endpoint="awards", year=year if isinstance(year, int) else False
                ),
                headers=self._headers,
            )
        )
        if isinstance(year, range):
            return [Award(**award_data) for award_data in response if award_data["year"] in year]
        else:
            return [Award(**award_data) for award_data in response]

    def years_participated(self) -> typing.List[int]:
        """
        Returns all the years this team has participated in.

        Returns:
            A list of integers representing every year this team has participated in.
        """
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url("team", key=self.key, endpoint="years_participated"), headers=self._headers
            )
        )
        return response

    def districts(self) -> typing.List[District]:
        """
        Retrieves a list of districts representing each year this team was in said district.

        If a team has never been in a district, the list will be empty.

        Returns:
            A list of districts representing each year this team was in said district if a team has participated in a district, otherwise returns an empty list.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("team", key=self.key, endpoint="districts"), headers=self._headers)
        )
        return [District(**district_data) for district_data in response]

    def matches(
        self,
        year: typing.Union[range, int],
        event_code: typing.Optional[str] = None,
        simple: typing.Optional[bool] = False,
        keys: typing.Optional[bool] = False,
    ) -> typing.List[Match]:
        """
        Retrieves all matches a team played from certain year(s).

        Parameters:
            year:
                An integer representing the year to retrieve a team's matches from or a range object representing all the years matches a team played should be retrieved from.
            event_code
                A string representing the code of an event (the latter half of a key, eg 'iri' instead of '2022iri'). Used for filtering matches a team played to only those in a certain event. Can be None if all matches a team played want to be retrieved.
            simple:
                A boolean representing whether each match's information should be stripped to only contain relevant information. Can be False if `simple` isn't passed in.
            keys:
                A boolean representing whether only the keys of the matches a team played from said year should be returned. Can be False if `keys` isn't passed in.

        Returns:
            A list of Match objects representing each match a team played based on the conditions; might be empty if team didn't play matches in the specified year(s).
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        if isinstance(year, range):
            return list(
                itertools.chain.from_iterable(
                    InternalData.loop.run_until_complete(
                        asyncio.gather(*[self.matches(spec_year, event_code, simple, keys) for spec_year in year])
                    )
                )
            )
        else:
            return InternalData.loop.run_until_complete(self._get_year_matches(year, event_code, simple, keys))

    def media(self, year: typing.Union[range, int], media_tag: typing.Optional[str] = None) -> typing.List[Media]:
        """
        Retrieves all the media of a certain team based off the parameters.

        Parameters:
            year:
                An integer representing a year to retrieve a team's media from or a range object representing all the years media from a team should be retrieved from.
            media_tag:
                A string representing the type of media to be returned. Can be None if media_tag is not passed in.

        Returns:
            A list of Media objects representing individual media from a team.
        """  # noqa
        if isinstance(year, range):
            return list(
                itertools.chain.from_iterable(
                    InternalData.loop.run_until_complete(
                        asyncio.gather(*[self.media(spec_year, media_tag) for spec_year in year])
                    )
                )
            )
        else:
            return InternalData.loop.run_until_complete(self._get_year_media(year, media_tag))

    def robots(self) -> typing.List[Robot]:
        """
        Retrieves a list of robots representing each robot for every year the team has played if they named the robot.

        If a team has never named a robot, the list will be empty.

        Returns:
            A list of districts representing each year this team was in said district if a team has named a robot, otherwise returns an empty list.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("team", key=self.key, endpoint="robots"), headers=self._headers)
        )
        return [Robot(**robot_data) for robot_data in response]

    def events(
        self,
        year: typing.Union[range, int] = None,
        simple: bool = False,
        keys: bool = False,
        statuses: bool = False,
    ) -> typing.Union[typing.List[typing.Union[Event, str]], typing.Dict[str, EventTeamStatus]]:
        """
        Retrieves and returns a record of events based on the parameters given.

        Parameters:
            year:
                An integer that specifies if only the events the team participated from that year should be retrieved.
                If year is a range object, it will return all events that the team participated in during that timeframe.
                If year is None, this method will return all events the team has ever participated in.
            simple:
                A boolean that specifies whether the results for each event should be 'shortened' and only contain more relevant information.
            keys:
                A boolean that specifies whether only the names of the events this team has participated in should be returned.
            statuses:
                A boolean that specifies whether a key/value pair of the statuses of teams in an event should be returned.

        Returns:
            A list of Event objects for each event that was returned or a list of strings representing the keys of the events or a dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")
        elif statuses and (simple or keys):
            raise ValueError(
                "statuses cannot be True in conjunction with simple or keys,"
                " if statuses is True then simple and keys must be False."
            )
        elif statuses and not year:
            raise ValueError("statuses cannot be True if a year isn't passed into Team.events.")
        elif statuses and isinstance(year, range):
            raise ValueError("statuses cannot be True when year is a range object.")

        if isinstance(year, range):
            return list(
                itertools.chain.from_iterable(
                    InternalData.loop.run_until_complete(
                        asyncio.gather(*[self.events(spec_year, simple, keys, statuses) for spec_year in year])
                    )
                )
            )
        else:
            return InternalData.loop.run_until_complete(self._get_year_events(year, simple, keys, statuses))

    def event(
        self,
        event_key: str,
        *,
        awards: bool = False,
        matches: bool = False,
        simple: bool = False,
        keys: bool = False,
        status: bool = False,
    ) -> typing.Union[typing.List[Award], EventTeamStatus, typing.List[typing.Union[Match, str]]]:
        """
        Retrieves and returns a record of teams based on the parameters given.

        Parameters:
            event_key:
                An event key (a unique key specific to one event) to retrieve data from.
            awards:
                A boolean that specifies whether the awards a team got during a match should be retrieved. Cannot be True in conjunction with `matches`.
            matches:
                A boolean that specifies whether the matches a team played in during an event should be retrieved. Cannot be True in conjunction with `awards`.
            simple:
                A boolean that specifies whether the results for each event's matches should be 'shortened' and only contain more relevant information. Do note that `simple` should only be True in conjunction with `matches`.
            keys:
                A boolean that specifies whether only the keys of the matches the team played should be returned. Do note that `keys` should only be True in conjunction with `matches`
            status:
                A boolean that specifies whether a key/value pair of the status of the team during an event should be returned. `status` should only be the only boolean out of the parameters that is True when using it.

        Returns:
            A list of Match objects representing each match a team played or an EventTeamStatus object to represent the team's status during an event or a list of strings representing the keys of the matches the team played in or a list of Award objects to represent award(s) a team got during an event.
        """  # noqa
        if not awards and not matches and not status:
            raise ValueError("Either awards, matches or status must be True for this function.")
        elif simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")
        elif awards and (simple or keys or matches):
            raise ValueError(
                "awards cannot be True in conjunction with simple, keys or matches, "
                "if awards is True then simple, keys, and matches must be False."
            )
        elif status and (simple or keys or matches):
            raise ValueError(
                "status cannot be True in conjunction with simple, keys or matches "
                "if statuses is True then simple, keys, and matches must be False."
            )

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                url=construct_url(
                    "team",
                    key=self.key,
                    endpoint="event",
                    event_key=event_key,
                    awards=awards,
                    matches=matches,
                    status=status,
                    simple=simple,
                    keys=keys,
                ),
                headers=self._headers,
            )
        )
        if matches and keys:
            return response
        elif matches:
            return [Match(**match_data) for match_data in response]
        elif awards:
            return [Award(**award_data) for award_data in response]
        else:
            return EventTeamStatus(event_key, response)

    def social_media(self) -> typing.List[Media]:
        """
        Retrieves all social media accounts of a team registered on TBA.

        Returns:
            A list of Media objects representing each social media account of a team. May be empty if a team has no social media accounts.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(url=construct_url("team", key=self.key, endpoint="social_media"), headers=self._headers)
        )
        return [Media(**social_media_info) for social_media_info in response]

    def __hash__(self) -> int:
        return self.team_number

    def __lt__(self, other: "Team") -> bool:
        return self.team_number < other.team_number
