import asyncio
import datetime
import functools
import itertools
import statistics
import typing
from dataclasses import dataclass
from json import dumps
from re import match
from statistics import mean

import aiohttp

from .award import Award
from .base_schema import BaseSchema
from .event_team_status import EventTeamStatus
from .match import Match
from .media import Media
from .robot import Robot

try:
    from utils import *
except ImportError:
    from ..falcon_alliance_utils import *

__all__ = ["District", "Event", "Team"]
PARSING_FORMAT = "%Y-%m-%d"


class District(BaseSchema):
    """Class representing a district containing methods to get specific district information.

    Attributes:
        key (str): 	Key for this district, e.g. 2022chs.
        year (int): Year this district participated.
        abbreviation (str): The short identifier for the district.
        display_name (str, optional): The long name for the district.
    """

    # Copied over from api_client.py because autocomplete doesn't work
    # when the decorator is in another file from the functions it decorates.
    def _caching_headers(func: typing.Callable) -> typing.Callable:
        """Decorator for utilizing the `Etag` and `If-None-Match` caching headers for the TBA API."""

        @functools.wraps(func)
        def wrapper(
            self, *args, use_caching: bool = False, etag: str = "", silent: bool = False, **kwargs
        ) -> typing.Any:
            """Wrapper for adding headers to cache the results from the TBA API."""

            self.use_caching = use_caching
            self.silent = silent

            self.etag = etag or self.etag

            try:
                return func(self, *args, **kwargs)
            except aiohttp.ContentTypeError:  # pragma: no cover
                if not silent:
                    raise NotModifiedSinceError from None
                else:
                    return_type = str(func.__annotations__["return"]).lower()

                    if "list" in return_type:
                        return []
                    elif "dict" in return_type:
                        return {}

        return wrapper

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

    @_caching_headers
    def events(
        self,
        simple: bool = False,
        keys: bool = False,
    ) -> typing.List[typing.Union[str, "Event"]]:
        """Retrieves a list of events in the given district.

        Args:
            simple (bool): A boolean that specifies whether the results for each event should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the keys of the events in a given district should be retrieved.

        Returns:
            typing.List[typing.Union[str, falcon_alliance.Event]]: A list of strings with each string representing an event's key for all the events in the given district or a list of Event objects with each object representing an event in the given district.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("district", key=self.key, endpoint="events", simple=simple, keys=keys),
                headers=self._headers,
            )
        )
        if keys:
            return response
        else:
            return [Event(**event_data) for event_data in response]

    @_caching_headers
    def teams(
        self,
        simple: bool = False,
        keys: bool = False,
    ) -> typing.List[typing.Union[str, "Team"]]:
        """Retrieves a list of teams in the given district.

        Args:
            simple (bool): A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the keys of the teams in a given district should be retrieved.

        Returns:
            typing.List[typing.Union[str, falcon_alliance.Team]]: A list of strings with each string representing a team's key for all the teams in the given district or a list of Team objects with each object representing a team in the given district.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("district", key=self.key, endpoint="teams", simple=simple, keys=keys),
                headers=self._headers,
            )
        )
        if keys:
            return response
        else:
            return [Team(**event_data) for event_data in response]

    @_caching_headers
    def rankings(self) -> typing.List[Ranking]:
        """
        Retrieves a list of team district rankings for the given district.

        Returns:
            typing.List[falcon_alliance.District.Ranking]: A list of Ranking objects with each Ranking object representing a team's district ranking for the given district.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("district", key=self.key, endpoint="rankings"),
                headers=self._headers,
            )
        )
        return [self.Ranking(**team_ranking_data) for team_ranking_data in response]


class Event(BaseSchema):
    """Class representing an event containing methods to get specific event information

    Attributes:
        key (str): TBA event key with the format yyyy[EVENT_CODE], where yyyy is the year, and EVENT_CODE is the event code of the event.
        name (str, optional): Official name of event on record either provided by FIRST or organizers of offseason event.
        event_code (str): Event short code, as provided by FIRST.
        event_type (int, optional): Event Type, as defined here: https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/event_type.py#L2
        district (District, optional): The district the event occurred in.
        city (str, optional): City, town, village, etc. the event is located in.
        state_prov (str, optional): State or Province the event is located in.
        country (str, optional): Country the event is located in.
        start_date (datetime.datetime, optional): Event start date in yyyy-mm-dd format.
        end_date (datetime.datetime, optional): Event end date in yyyy-mm-dd format.
        year (int): Year the event data is for.
        short_name (str, optional): Same as name but doesn't include event specifiers, such as 'Regional' or 'District'. May be None.
        event_type_string (str): Event Type, eg Regional, District, or Offseason.
        week (int, optional): Week of the event relative to the first official season event, zero-indexed. Only valid for Regionals, Districts, and District Championships. Equal to None otherwise. (Eg. A season with a week 0 'preseason' event does not count, and week 1 events will show 0 here. Seasons with a week 0.5 regional event will show week 0 for those event(s) and week 1 for week 1 events and so on.)
        address (str, optional): Address of the event's venue, if available.
        postal_code (str, optional): Postal code from the event address.
        gmaps_place_id (str, optional): Google Maps Place ID for the event address.
        gmaps_url (str, optional): Link to address location on Google Maps.
        lat (float, optional): Latitude for the event address.
        lng (float, optional): Longitude for the event address.
        location_name (str, optional): Name of the location at the address for the event, eg. Blue Alliance High School.
        timezone (str, optional): Timezone name.
        website (str, optional): The event's website, if any.
        first_event_id (str, optional): The FIRST internal Event ID, used to link to the event on the FRC webpage.
        first_event_code (str, optional): Public facing event code used by FIRST (on frc-events.firstinspires.org, for example)
        webcasts (list[falcon_alliance.Event.Webcast, optional): A list of all webcasts recording the event.
        division_keys (list, optional): A list of event keys for the divisions of the event.
        parent_event_key (str, optional): The TBA Event key that represents the event's parent. Used to link back to the event from a division event. It is also the inverse relation of divison_keys.
        playoff_type (int, optional): Playoff Type, as defined here: https://github.com/the-blue-alliance/the-blue-alliance/blob/master/consts/playoff_type.py#L4, or None.
        playoff_type_string (str, optional): String representation of the playoff_type, or None.
    """  # noqa

    # Copied over from other classes in main_schemas.py as autocomplete fails to work
    # when the decorator is defined in another class.
    def _caching_headers(func: typing.Callable) -> typing.Callable:
        """Decorator for utilizing the `Etag` and `If-None-Match` caching headers for the TBA API."""

        @functools.wraps(func)
        def wrapper(
            self, *args, use_caching: bool = False, etag: str = "", silent: bool = False, **kwargs
        ) -> typing.Any:
            """Wrapper for adding headers to cache the results from the TBA API."""

            self.use_caching = use_caching
            self.silent = silent

            self.etag = etag or self.etag

            try:
                return func(self, *args, **kwargs)
            except aiohttp.ContentTypeError:  # pragma: no cover
                if not silent:
                    raise NotModifiedSinceError from None
                else:
                    return_type = str(func.__annotations__["return"]).lower()

                    if "list" in return_type:
                        return []
                    elif "dict" in return_type:
                        return {}

        return wrapper

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
            """Gets the average of all the metrics for said event; could also only get one average for a specific metric if you aren't interested in all metrics.

            Args:
                metric (str): A string representing which metric to get the average for (opr/dpr/ccwm). `metric` is optional, and if not passed in, the averages for all metrics will be retrieved.

            Returns:
                typing.Union[dict, float]: A dictionary containing the averages for all metrics or a decimal (float object) representing the average of one of the metrics if specified.
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

    @_caching_headers
    def alliances(self) -> typing.List[Alliance]:
        """Retrieves all alliances of an event.

        Returns:
            typing.List[falcon_alliance.Event.Alliance]: A list of Alliance objects representing each alliance in the event.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("event", key=self.key, endpoint="alliances"),
                headers=self._headers,
            )
        )
        return [self.Alliance(**alliance_info) for alliance_info in response]

    @_caching_headers
    def awards(self) -> typing.List[Award]:
        """Retrieves all awards distributed in an event.

        Returns:
            typing.List[falcon_alliance.Award]: A list of Award objects representing each award distributed in an event.
        """
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("event", key=self.key, endpoint="awards"),
                headers=self._headers,
            )
        )
        return [Award(**award_info) for award_info in response]

    @_caching_headers
    def district_points(self) -> typing.Optional[DistrictPoints]:
        """Retrieves district points for teams during an event for both qualification and tiebreaker matches.

        Returns:
            typing.Optional[typing.Event.DistrictPoints]: A DistrictPoints object containing "points" and "tiebreakers" fields, with each field possessing a dictionary mapping team keys to their points or None if the event doesn't take place in a district or district points are not applicable to the event.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("event", key=self.key, endpoint="district_points"),
                headers=self._headers,
            )
        )

        if response:
            return self.DistrictPoints(**response)

    @_caching_headers
    def insights(self) -> typing.Optional[Insights]:
        """Retrieves insights of an event (specific data about performance and the like at the event; specific by game).
        Insights can only be retrieved for any events from 2016 and onwards.

        Returns:
            typing.Optional[falcon_alliance.Event.Insights]: An Insight object containing qualification and playoff insights from the event. Can be None if the event hasn't occurred yet, and the fields of Insight may be None depending on how far the event has advanced.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("event", key=self.key, endpoint="insights"),
                headers=self._headers,
            )
        )

        if response:
            return self.Insights(**response)

    @_caching_headers
    def matches(
        self, simple: bool = False, keys: bool = False, timeseries: bool = False
    ) -> typing.List[typing.Union[str, Match]]:
        """Retrieves all matches that occurred during an event.

        Per TBA, the timeseries data is in development and therefore you should NOT rely on it.

        Args:
            simple (bool): A boolean that specifies whether the results for each match should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the keys of the matches should be retrieved.
            timeseries (bool): A boolean that specifies whether only the keys of the matches that have timeseries data should be retrieved.

        Returns:
            typing.List[typing.Union[str, falcon_alliance.Match]]: A dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary or a list of strings representing the keys of the teams that participated in an event or a list of Team objects, each representing a team that participated in an event.
        """  # noqa
        if (simple, keys, timeseries).count(True) > 1:
            raise ValueError(
                "Only one parameter out of `simple`, `keys`, and `timeseries`"
                " can be True. You can't mix and match parameters."
            )

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
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

    @_caching_headers
    def oprs(self) -> OPRs:
        """Retrieves different metrics for all teams during an event.
        To see an explanation on OPR and other metrics retrieved from an event, see https://www.thebluealliance.com/opr.

        Returns:
            falcon_alliance.Event.OPRs: An OPRs object containing a key/value pair for the OPRs, DPRs, and CCWMs of all teams at an event. The fields of `OPRs` may be empty if OPRs, DPRs, and CCWMs weren't calculated.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self, url=construct_url("event", key=self.key, endpoint="oprs"), headers=self._headers
            )
        )

        if response:
            return self.OPRs(**response)
        else:  # pragma: no cover
            return self.OPRs(oprs={}, dprs={}, ccwms={})

    @_caching_headers
    def predictions(self) -> dict:
        """Retrieves predictions for matches of an event. May not work for all events since this endpoint is in beta per TBA.

        Returns:
            dict: A dictionary containing the predictions of an event from TBA (contains year-specific information). May be an empty dictionary if there are no predictions available for that event.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("event", key=self.key, endpoint="predictions"),
                headers=self._headers,
            )
        )
        return response

    @_caching_headers
    def rankings(self) -> typing.Dict[str, Ranking]:
        """Retrieves a list of team rankings for an event.

        Returns:
            typing.Dict[str, falcon_alliance.Event.Ranking]: A dictionary with team keys as the keys of the dictionary and Ranking objects for that team's information about their ranking at an event as values of the dictionary.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("event", key=self.key, endpoint="rankings"),
                headers=self._headers,
            )
        )
        rankings_dict = {}

        for rank_info in response["rankings"]:
            rank_info["extra_stats"] = self.ExtraStats(rank_info["extra_stats"], response["extra_stats_info"])
            rank_info["sort_orders"] = self.SortOrders(rank_info["sort_orders"], response["sort_order_info"])

            rankings_dict[rank_info["team_key"]] = self.Ranking(**rank_info)

        return rankings_dict

    @_caching_headers
    def teams(
        self, simple: bool = False, keys: bool = False, statuses: bool = False
    ) -> typing.Union[typing.List[typing.Union[str, "Team"]], typing.Dict[str, EventTeamStatus]]:
        """
        Retrieves all teams who participated at an event.

        Args:
            simple (bool): A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the names of the FRC teams should be retrieved.
            statuses (bool): A boolean that specifies whether a key/value pair of the statuses of teams in an event should be returned.

        Returns:
            typing.Union[typing.List[typing.Union[str, falcon_alliance.Team]], typing.Dict[str, falcon_alliance.EventTeamStatus]]: A dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary or a list of strings representing the keys of the teams that participated in an event or a list of Team objects, each representing a team that participated in an event.
        """  # noqa
        if (simple, keys, statuses).count(True) > 1:
            raise ValueError(
                "Only one parameter out of `simple`, `keys`, and `statuses` can be True."
                " You can't mix and match parameters."
            )

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
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

    def min(self, metric: Metrics) -> typing.Union[Match, tuple[float, "Team"]]:
        """
        Retrieves the minimum of a certain metric based on the year.

        Args:
            metric (Metrics): An Enum object representing which metric to use to find the minimum of something relating to a team of your desire.

        Returns:
            typing.Union[Match, tuple[float, falcon_alliance.Team]]: A Match object representing the match with the minimum cumulative score (red alliance's score + blue alliance's score) if Metrics.MATCH_SCORE is passed into `metric` or a tuple containing the float representing the minimum OPR/DPR/CCWM during an event and a Team object representing the team that had the minimum OPR.
        """  # noqa
        if metric == Metrics.MATCH_SCORE:
            event_matches = self.matches()
            return min(event_matches, key=lambda match: match.alliances["red"].score + match.alliances["blue"].score)
        elif metric in {Metrics.OPR, Metrics.DPR, Metrics.CCWM}:
            team_key, opr = min(getattr(self.oprs(), f"{metric._name_.lower()}s").items(), key=lambda tup: tup[1])
            return opr, Team(team_key)

    def max(self, metric: Metrics) -> typing.Union[Match, tuple[float, "Team"]]:
        """
        Retrieves the maximum of a certain metric based on the year.

        Args:
            metric (Metrics): An Enum object representing which metric to use to find the maximum of something relating to a team of your desire.

        Returns:
            typing.Union[Match, tuple[float, falcon_alliance.Team]]: A Match object representing the match with the maximum cumulative score (red alliance's score + blue alliance's score) if Metrics.MATCH_SCORE is passed into `metric` or a tuple containing the float representing the maximum OPR/DPR/CCWM during an event and a Team object representing the team that had the maximum OPR.
        """  # noqa
        if metric == Metrics.MATCH_SCORE:
            event_matches = self.matches()
            return max(event_matches, key=lambda match: match.alliances["red"].score + match.alliances["blue"].score)
        elif metric in {Metrics.OPR, Metrics.DPR, Metrics.CCWM}:
            team_key, opr = max(getattr(self.oprs(), f"{metric._name_.lower()}s").items(), key=lambda tup: tup[1])
            return opr, Team(team_key)

    def average(self, metric: Metrics) -> float:
        """
        Retrieves the aveage of a certain metric based on the year.

        Args:
            metric (Metrics): An Enum object representing which metric to use to find the average of something relating to a team of your desire.

        Returns:
            float: A float representing the average match score if Metrics.MATCH_SCORE is passed into `metric` or a float representing the average OPR/DPR/CCWM.
        """  # noqa
        if metric == Metrics.MATCH_SCORE:
            event_scores = [alliance.score for match in self.matches() for alliance in match.alliances.values()]
            return statistics.mean(event_scores)
        elif metric in {Metrics.OPR, Metrics.DPR, Metrics.CCWM}:
            return statistics.mean(getattr(self.oprs(), f"{metric._name_.lower()}s").values())

    def update_info(self, data: dict) -> None:
        """
        POST request to update info for an event.

        Parameters:
            data (dict): Dictionary containing info that the event needs to be updated with (eg FIRST code, playoff type, and webcast URLs).
        """  # noqa
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/info/update",
                data=dumps(data),
            )
        )

    def update_alliance_selections(self, data: typing.List[list]) -> None:
        """
        POST request to update info about alliance selections for an event.

        Parameters:
            data (list[list]): 2D list with each list representing an alliance and the elements inside each sublist representing keys in the corresponding alliance.
        """  # noqa
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/alliance_selections/update",
                data=dumps(data),
            )
        )

    def update_awards(self, data: typing.List[dict]) -> None:
        """
        POST request to update info regarding awards for an event.

        Parameters:
            data (list[dict]): List of dictionaries containing information about each award (eg name of the award, recipient of the award, and the awardee).
        """  # noqa
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/awards/update",
                data=dumps(data),
            )
        )

    def update_matches(self, data: typing.List[dict]) -> None:
        """
        POST request to update info regarding matches for an event.

        Parameters:
            data (list[dict]): List of dictionaries containing information about each match.
        """
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/matches/update",
                data=dumps(data),
            )
        )

    def delete_matches(self, data: typing.List[str]) -> None:
        """
        POST request to delete matches by match keys for an event.

        Parameters:
            data (list[str]): List of matches to delete (eg ["qm1", "qm2", ...])
        """
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/matches/delete",
                data=dumps(data),
            )
        )

    def update_team_list(self, data: typing.List[str]) -> None:
        """
        POST request to update the team list for an event.
        Parameters:
            data (list[str]): List containing the keys of each team at the event.
        """
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/team_list/update",
                data=dumps(data),
            )
        )

    def update_match_videos(self, data: dict) -> None:
        """
        POST request to update the match videos for an event.
        Parameters:
            data (dict): Mapping of partial match keys (i.e. qm1) to YouTube video IDs.
        """
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/match_videos/update",
                data=dumps(data),
            )
        )

    def update_media(self, data: typing.List[str]) -> None:
        """
        POST request to update the media for an event.
        Parameters:
            data (list[str]): List of YouTube video IDs to add as media for an event.
        """
        InternalData.loop.run_until_complete(
            InternalData.post(
                self,
                url=f"https://www.thebluealliance.com/api/trusted/v1/event/{self.key}/media/update",
                data=dumps(data),
            )
        )


class Team(BaseSchema):
    """Class representing a team's metadata with methods to get team specific data.

    Attributes:
        key (str): TBA team key with the format frcXXXX with XXXX representing the team number.
        team_number (int): Official team number issued by FIRST.
        nickname (str, optional): Team nickname provided by FIRST.
        name (str, optional): Official long name registered with FIRST.
        school_name (str, optional): Name of team school or affilited group registered with FIRST.
        city (str, optional): City of team derived from parsing the address registered with FIRST.
        state_prov (str, optional): State of team derived from parsing the address registered with FIRST.
        country (str, optional): Country of team derived from parsing the address registered with FIRST.
        address (str, optional): Will be None, for future development.
        postal_code (str, optional): Postal code from the team address.
        gmaps_place_id (str, optional): Will be None, for future development.
        gmaps_url (str, optional): Will be None, for future development.
        lat (float, optional): Will be None, for future development.
        lng (float, optional): Will be None, for future development.
        location_name (str, optional): Will be None, for future development.
        website (str, optional): Official website associated with the team.
        rookie_year (int, optional): First year the team officially competed.
        motto (str, optional): Team's motto as provided by FIRST. This field is deprecated and will return None - will be removed at end-of-season in 2019.
        home_championship (dict, optional): Location of the team's home championship each year as a key-value pair. The year (as a string) is the key, and the city is the value.
    """  # noqa

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

    # Copied over from other classes in main_schemas.py as autocomplete fails to work
    # when the decorator is defined in another class.
    def _caching_headers(func: typing.Callable) -> typing.Callable:
        """Decorator for utilizing the `Etag` and `If-None-Match` caching headers for the TBA API."""

        @functools.wraps(func)
        def wrapper(
            self, *args, use_caching: bool = False, etag: str = "", silent: bool = False, **kwargs
        ) -> typing.Any:
            """Wrapper for adding headers to cache the results from the TBA API."""

            self.use_caching = use_caching
            self.silent = silent

            self.etag = etag or self.etag

            try:
                return func(self, *args, **kwargs)
            except aiohttp.ContentTypeError:
                if not silent:
                    raise NotModifiedSinceError from None
                else:
                    return_type = str(func.__annotations__["return"]).lower()

                    if "list" in return_type:
                        return []
                    elif "dict" in return_type:  # pragma: no cover
                        return {}

        return wrapper

    @_caching_headers
    async def _get_year_events(
        self, year: int, simple: bool, keys: bool, statuses: bool
    ) -> typing.Union[typing.List[typing.Union[str, Event]], typing.Dict[str, EventTeamStatus]]:
        """
        Retrieves and returns all events from a year based on the parameters given.

        Args:
            year (int): An integer that specifies if only the events the team participated from that year should be retrieved.
            simple (bool): A boolean that specifies whether the results for each event should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the names of the events this team has participated in should be returned.
            statuses (bool): A boolean that specifies whether a key/value pair of the statuses of teams in an event should be returned.

        Returns:
            typing.Union[typing.List[typing.Union[str, falcon_alliance.Event]], typing.Dict[str, falcon_alliance.EventTeamStatus]]: A list of Event objects for each event that was returned or a list of strings representing the keys of the events or a dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary.
        """  # noqa
        response = await InternalData.get(
            current_instance=self,
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

    @_caching_headers
    async def _get_year_matches(
        self, year: int, event_code: typing.Optional[str], simple: bool, keys: bool
    ) -> typing.List[Match]:
        """
        Retrieves all matches a team played from a certain year.

        Args:
            year (int): An integer representing the year to retrieve a team's matches from.
            event_code (str): A string representing the code of an event (the latter half of a key, eg 'iri' instead of '2022iri'). Used for filtering matches a team played to only those in a certain event.
            simple (bool): A boolean representing whether each match's information should be stripped to only contain relevant information.
            keys (bool): A boolean representing whether only the keys of the matches a team played from said year should be returned:

        Returns:
            typing.List[falcon_alliance.Match]: A list of Match objects representing each match a team played based on the conditions; might be empty if team didn't play matches that year.
        """  # noqa
        response = await InternalData.get(
            current_instance=self,
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

    @_caching_headers
    async def _get_year_media(self, year: int, media_tag: typing.Optional[str] = None) -> typing.List[Media]:
        """
        Retrieves all the media of a certain team from a certain year and based off the media_tag if passed in.

        Args:
            year (int): An integer representing a year to retrieve a team's media from.
            media_tag (str): A string representing the type of media to be returned. Can be None if media_tag is not passed in.

        Returns:
            typing.List[falcon_alliance.Media]: A list of Media objects representing individual media from a team during a year.
        """  # noqa
        if media_tag:
            url = construct_url(
                "team", key=self.key, endpoint="media", second_endpoint="tag", media_tag=media_tag, year=year
            )
        else:
            url = construct_url("team", key=self.key, endpoint="media", year=year)

        response = await InternalData.get(current_instance=self, url=url, headers=self._headers)
        return [Media(**media_data) for media_data in response]

    @_caching_headers
    def awards(self, year: typing.Optional[typing.Union[range, int]] = None) -> typing.List[Award]:
        """
        Retrieves all awards a team has gotten either during its career or during certain year(s).

        Args:
            year (int, range, optional): An integer representing a year that the awards should be returned for or a range object representing the years that awards should be returned from. Can be None if no year is passed in as it is an optional parameter.

        Returns:
            typing.List[falcon_alliance.Award]: A list of Award objects representing each award a team has got based on the parameters; may be empty if the team has gotten no awards.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
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

    @_caching_headers
    def years_participated(self) -> typing.List[int]:
        """Returns all the years this team has participated in."""
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("team", key=self.key, endpoint="years_participated"),
                headers=self._headers,
            )
        )
        return response

    @_caching_headers
    def districts(self) -> typing.List[District]:
        """
        Retrieves a list of districts representing each year this team was in said district.

        If a team has never been in a district, the list will be empty.

        Returns:
            typing.List[falcon_alliance.District]: A list of districts representing each year this team was in said district if a team has participated in a district, otherwise returns an empty list.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("team", key=self.key, endpoint="districts"),
                headers=self._headers,
            )
        )
        return [District(**district_data) for district_data in response]

    @_caching_headers
    def matches(
        self,
        year: typing.Union[range, int],
        event_code: typing.Optional[str] = None,
        simple: typing.Optional[bool] = False,
        keys: typing.Optional[bool] = False,
    ) -> typing.List[Match]:
        """
        Retrieves all matches a team played from certain year(s).

        Args:
            year (int, range): An integer representing the year to retrieve a team's matches from or a range object representing all the years matches a team played should be retrieved from.
            event_code (str): A string representing the code of an event (the latter half of a key, eg 'iri' instead of '2022iri'). Used for filtering matches a team played to only those in a certain event. Can be None if all matches a team played want to be retrieved.
            simple (bool): A boolean representing whether each match's information should be stripped to only contain relevant information. Can be False if `simple` isn't passed in.
            keys (bool): A boolean representing whether only the keys of the matches a team played from said year should be returned. Can be False if `keys` isn't passed in.

        Returns:
            typing.List[falcon_alliance.Match]: A list of Match objects representing each match a team played based on the conditions; might be empty if team didn't play matches in the specified year(s).
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        if isinstance(year, range):
            return list(
                itertools.chain.from_iterable(
                    InternalData.loop.run_until_complete(
                        asyncio.gather(
                            *[
                                self._get_year_matches(
                                    spec_year,
                                    event_code,
                                    simple,
                                    keys,
                                    use_caching=self.use_caching,
                                    etag=self.etag,
                                    silent=self.silent,
                                )
                                for spec_year in year
                            ]
                        )
                    )
                )
            )
        else:
            return InternalData.loop.run_until_complete(
                self._get_year_matches(
                    year, event_code, simple, keys, use_caching=self.use_caching, etag=self.etag, silent=self.silent
                )
            )

    @_caching_headers
    def media(self, year: typing.Union[range, int], media_tag: typing.Optional[str] = None) -> typing.List[Media]:
        """
        Retrieves all the media of a certain team based off the parameters.

        Args:
            year (int, range): An integer representing a year to retrieve a team's media from or a range object representing all the years media from a team should be retrieved from.
            media_tag (str): A string representing the type of media to be returned. Can be None if media_tag is not passed in.

        Returns:
            typing.List[falcon_alliance.Media]: A list of Media objects representing individual media from a team.
        """  # noqa
        if isinstance(year, range):
            return list(
                itertools.chain.from_iterable(
                    InternalData.loop.run_until_complete(
                        asyncio.gather(
                            *[
                                self._get_year_media(
                                    spec_year,
                                    media_tag,
                                    use_caching=self.use_caching,
                                    etag=self.etag,
                                    silent=self.silent,
                                )
                                for spec_year in year
                            ]
                        )
                    )
                )
            )
        else:
            return InternalData.loop.run_until_complete(
                self._get_year_media(year, media_tag, use_caching=self.use_caching, etag=self.etag, silent=self.silent)
            )

    @_caching_headers
    def robots(self) -> typing.List[Robot]:
        """
        Retrieves a list of robots representing each robot for every year the team has played if they named the robot.

        If a team has never named a robot, the list will be empty.

        Returns:
            typing.List[falcon_alliance.Robot]: A list of robots representing each year a team has registered its robot onto TBA, if a team hasn't named a robot before it returns an empty list.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self, url=construct_url("team", key=self.key, endpoint="robots"), headers=self._headers
            )
        )
        return [Robot(**robot_data) for robot_data in response]

    @_caching_headers
    def events(
        self,
        year: typing.Union[range, int] = None,
        simple: bool = False,
        keys: bool = False,
        statuses: bool = False,
    ) -> typing.Union[typing.List[typing.Union[Event, str]], typing.Dict[str, EventTeamStatus]]:
        """
        Retrieves and returns a record of events based on the parameters given.

        Args:
            year (int, range, optional): An integer that specifies if only the events the team participated from that year should be retrieved. If year is a range object, it will return all events that the team participated in during that timeframe. If year isn't passed in, this method will return all events the team has ever participated in.
            simple (bool): A boolean that specifies whether the results for each event should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the names of the events this team has participated in should be returned.
            statuses (bool): A boolean that specifies whether a key/value pair of the statuses of teams in an event should be returned.

        Returns:
            typing.Union[typing.List[typing.Union[falcon_alliance.Event, str]], typing.Dict[str, falcon_alliance.EventTeamStatus]]: A list of Event objects for each event that was returned or a list of strings representing the keys of the events or a dictionary with team keys as the keys of the dictionary and an EventTeamStatus object representing the status of said team as the values of the dictionary.
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
                        asyncio.gather(
                            *[
                                self._get_year_events(
                                    spec_year,
                                    simple,
                                    keys,
                                    statuses,
                                    use_caching=self.use_caching,
                                    etag=self.etag,
                                    silent=self.silent,
                                )
                                for spec_year in year
                            ]
                        )
                    )
                )
            )
        else:
            return InternalData.loop.run_until_complete(
                self._get_year_events(
                    year, simple, keys, statuses, use_caching=self.use_caching, etag=self.etag, silent=self.silent
                )
            )

    @_caching_headers
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

        Args:
            event_key (str): An event key (a unique key specific to one event) to retrieve data from.
            awards (bool): A boolean that specifies whether the awards a team got during a match should be retrieved. Cannot be True in conjunction with `matches`.
            matches (bool): A boolean that specifies whether the matches a team played in during an event should be retrieved. Cannot be True in conjunction with `awards`.
            simple (bool): A boolean that specifies whether the results for each event's matches should be 'shortened' and only contain more relevant information. Do note that `simple` should only be True in conjunction with `matches`.
            keys (bool): A boolean that specifies whether only the keys of the matches the team played should be returned. Do note that `keys` should only be True in conjunction with `matches`
            status (bool): A boolean that specifies whether a key/value pair of the status of the team during an event should be returned. `status` should only be the only boolean out of the parameters that is True when using it.

        Returns:
            typing.Union[typing.List[falcon_alliance.Award], falcon_alliance.EventTeamStatus, typing.List[typing.Union[falcon_alliance.Match, str]]]: A list of Match objects representing each match a team played or an EventTeamStatus object to represent the team's status during an event or a list of strings representing the keys of the matches the team played in or a list of Award objects to represent award(s) a team got during an event.
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
                current_instance=self,
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

    @_caching_headers
    def social_media(self) -> typing.List[Media]:
        """
        Retrieves all social media accounts of a team registered on TBA.

        Returns:
            typing.List[falcon_alliance.Media]: A list of Media objects representing each social media account of a team. May be empty if a team has no social media accounts.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url("team", key=self.key, endpoint="social_media"),
                headers=self._headers,
            )
        )
        return [Media(**social_media_info) for social_media_info in response]

    def min(
        self, year: typing.Union[range, int], metric: Metrics, *, event_code: typing.Optional[str] = None
    ) -> typing.Union[Match, typing.Tuple[float, Event]]:
        """
        Retrieves the minimum of a certain metric based on the year.

        Args:
            year (range, int): An integer representing the year to apply the metric to or a range object representing the years to apply the metric to.
            metric (Metrics): An Enum object representing which metric to use to find the minimum of something relating to a team of your desire.
            event_code(str, optional): A string representing which event to apply a certain metric to for finding the minimum based on said metric (optional).

        Returns:
            typing.Union[Match, tuple[float, falcon_alliance.Event]]: A Match object representing the match with the minimum score if Metrics.MATCH_SCORE is passed into `metric` or a tuple containing the minimum OPR/DPR/CCWM for a team and the event where the team had said minimum OPR/DPR/CCWM if Metrics.OPR, Metrics.DPR or Metrics.CCWM is passed into `metric`.
        """  # noqa
        if metric == Metrics.MATCH_SCORE:
            team_matches = self.matches(year, event_code) if event_code else self.matches(year)
            return min(team_matches, key=lambda match: match.alliance_of(self.key).score)
        elif metric in {Metrics.OPR, Metrics.DPR, Metrics.CCWM}:
            if event_code:
                raise ValueError(f"`event_code` parameter incompatible with the metric {metric}.")

            team_oprs = []

            for event in self.events(year):
                event_oprs = event.oprs()

                if getattr(event_oprs, f"{metric.name.lower()}s"):
                    team_oprs.append((getattr(event_oprs, f"{metric.name.lower()}s")[self.key], event))

            return min(team_oprs, key=lambda tup: tup[0])
        else:
            raise ValueError(f"{metric} incompatible with `Team.min`.")

    def max(
        self, year: typing.Union[range, int], metric: Metrics, *, event_code: typing.Optional[str] = None
    ) -> typing.Union[Match, typing.Tuple[float, Event]]:
        """
        Retrieves the maximum of a certain metric based on the year.

        Args:
            year (range, int): An integer representing the year to apply the metric to or a range object representing the years to apply the metric to.
            metric (Metrics): An Enum object representing which metric to use to find the maximum of something relating to a team of your desire.
            event_code(str, optional): A string representing which event to apply a certain metric to for finding the maximum based on said metric (optional).

        Returns:
            typing.Union[Match, tuple[float, falcon_alliance.Event]]: A Match object representing the match with the maximum score if Metrics.MATCH_SCORE is passed into `metric` or a tuple containing the maximum OPR/DPR/CCWM for a team and the event where the team had said maximum OPR/DPR/CCWM if Metrics.OPR, Metrics.DPR or Metrics.CCWM is passed into `metric`.
        """  # noqa
        if metric == Metrics.MATCH_SCORE:
            team_matches = self.matches(year, event_code) if event_code else self.matches(year)
            return max(team_matches, key=lambda match: match.alliance_of(self.key).score)
        elif metric in {Metrics.OPR, Metrics.DPR, Metrics.CCWM}:
            if event_code:
                raise ValueError(f"`event_code` parameter incompatible with the metric {metric}.")

            team_oprs = []

            for event in self.events(year):
                event_oprs = event.oprs()

                if getattr(event_oprs, f"{metric.name.lower()}s"):
                    team_oprs.append((getattr(event_oprs, f"{metric.name.lower()}s")[self.key], event))

            return max(team_oprs, key=lambda tup: tup[0])
        else:
            raise ValueError(f"{metric} incompatible with `Team.max`.")

    def average(
        self, year: typing.Union[range, int], metric: Metrics, *, event_code: typing.Optional[str] = None
    ) -> float:
        """
        Retrieves the average of a certain metric based on the year.

        Args:
            year (range, int): An integer representing the year to apply the metric to or a range object representing the years to apply the metric to.
            metric (Metrics): An Enum object representing which metric to use to find the average of something relating to a team of your desire.
            event_code(str, optional): A string representing which event to apply a certain metric to for finding the maximum based on said metric (optional).

        Returns:
            float: A float representing the average match score if Metrics.MATCH_SCORE is passed into `metric` or a float representing the average OPR/DPR/CCWM of a team for a certain year.
        """  # noqa
        if metric == Metrics.MATCH_SCORE:
            team_matches = self.matches(year, event_code) if event_code else self.matches(year)
            return statistics.mean([match.alliance_of(self).score for match in team_matches])
        elif metric in {Metrics.OPR, Metrics.DPR, Metrics.CCWM}:
            if event_code:
                raise ValueError(f"`event_code` parameter incompatible with the metric {metric}.")

            team_oprs = []

            for event in self.events(year):
                event_oprs = event.oprs()

                if getattr(event_oprs, f"{metric.name.lower()}s"):
                    team_oprs.append(getattr(event_oprs, f"{metric.name.lower()}s")[self.key])

            return statistics.mean(team_oprs)
        else:
            raise ValueError(f"{metric} incompatible with `Team.average`.")

    def location(self) -> typing.Optional[typing.Tuple[float, float]]:
        """
        Retrieves the location of the team based on its postal code.

        Returns:
            typing.Optional[typing.Tuple[float, float]]: Returns a tuple containing the latitude and longitude or None if it couldn't find a location for the team.
        """  # noqa
        if self.city or self.state_prov or self.country:
            if self.country in {"USA", "Canada"}:
                to_search = ", ".join([value for value in (self.city, self.state_prov, self.country) if value])
            else:
                to_search = ", ".join([value for value in (self.city, self.country) if value])

            geolocation = InternalData.loop.run_until_complete(
                InternalData.get(
                    current_instance=self,
                    url=f"https://nominatim.openstreetmap.org/search/{to_search}?format=json",
                    headers=self._headers,
                )
            )
        else:
            return

        try:
            return float(geolocation[0]["lat"]), float(geolocation[0]["lon"])
        except IndexError:  # when it can't find a location for the team.
            return

    def __hash__(self) -> int:
        return self.team_number

    def __lt__(self, other: "Team") -> bool:
        return self.team_number < other.team_number
