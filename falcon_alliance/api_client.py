import asyncio
import functools
import itertools
import os
import typing
from json import dumps
from types import TracebackType

import aiohttp
from dotenv import load_dotenv

from .schemas import *
from .utils import *

__all__ = ["ApiClient"]

load_dotenv()


class ApiClient:
    """Base class that contains all requests to the TBA API.

    Examples:
        If your API key isn't defined in your .env as `TBA_API_KEY` or `API_KEY`:

        >>> with ApiClient(api_key=your_api_key) as api_client:
        ...     print(api_client.team(4099).key)
        frc4099

        otherwise if it is:

        >>> with ApiClient() as api_client:
        ...     print(api_client.team(4099).key)
        frc4099

        All code, regardless of if it uses `ApiClient`'s methods or not must be in this context manager. For example:

        >>> with ApiClient():
        ...     print(Team(4099).event("2022iri", matches=True, keys=True))
        ["2022iri_f1m1", "2022iri_f1m2", ...]
    """

    def __init__(self, api_key: str = None, auth_secret: str = ""):
        if api_key is None:
            try:
                api_key = os.environ["TBA_API_KEY"]
            except KeyError:  # pragma: no cover
                # If TBA_API_KEY isn't an environment variable
                api_key = os.environ["API_KEY"]

        self._headers = {"X-TBA-Auth-Key": api_key}
        self.auth_secret = auth_secret
        self.etag = ""
        BaseSchema.add_headers(self._headers)
        BaseSchema.add_auth_secret(auth_secret)
        InternalData.loop.run_until_complete(InternalData.set_session())

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        self.close()

    def _caching_headers(func: typing.Callable) -> typing.Callable:
        """Decorator for utilizing the `Etag` and `If-None-Match` caching headers for the TBA API."""

        @functools.wraps(func)
        def wrapper(
            self, *args, use_caching: bool = False, etag: str = "", silent: bool = False, **kwargs
        ) -> typing.Any:
            """Wrapper for adding headers to cache the results from the TBA API."""

            self.use_caching = use_caching
            self.silent = silent

            if etag:
                self.etag = etag

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

    def close(self) -> None:
        """Closes the ongoing session (`aiohttp.ClientSession`)."""
        InternalData.loop.run_until_complete(self._close())

    async def _close(self) -> None:
        """Asynchronous helper function for closing the ongoing session (`aiohttp.ClientSession`)."""
        await InternalData.session.close()
        InternalData.session = None

    @_caching_headers
    async def _get_year_events(
        self, year: int, simple: bool = False, keys: bool = False
    ) -> typing.List[typing.Union[Event, str]]:
        """
        Retrieves all the events from a year.

        Parameters:
            year (int): An integer representing which year to return its events for.
            simple (bool): A boolean representing whether some of the information regarding an event should be stripped to only contain relevant information about the event.
            keys (bool): A boolean representing whether only the keys of the events should be returned.

        Returns:
            typing.List[typing.Union[falcon_alliance.Event, str]]: A list of Event objects representing each event in a year or a list of strings representing all the keys of the events retrieved.
        """  # noqa
        response = await InternalData.get(
            current_instance=self,
            url=construct_url("events", year=year, simple=simple, keys=keys),
            headers=self._headers,
        )
        if keys:
            return response
        else:
            return [Event(**event_data) for event_data in response]

    @_caching_headers
    async def _get_team_page(
        self,
        page_num: typing.Optional[int] = None,
        year: typing.Union[range, int] = None,
        simple: bool = False,
        keys: bool = False,
    ) -> typing.List[typing.Union[Team, str]]:
        """
        Returns a page of teams (a list of 500 teams or less)

        Parameters:
            page_num (int, optional): An integer that specifies the page number of the list of teams that should be retrieved. Teams are paginated by groups of 500, and if page_num is None, every team will be retrieved.
            year (int, range, optional): An integer that specifies if only the teams that participated during that year should be retrieved. If year is a range object, it will return all teams that participated in the years within the range object. If year is None, this method will get all teams that have ever participated in the history of FRC.
            simple (bool): A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the names of the FRC teams should be retrieved.

        Returns:
            typing.List[typing.Union[falcon_alliance.Team, str]]: A list of Team objects for each team in the list.
        """  # noqa
        if page_num is not None:
            response = await InternalData.get(
                current_instance=self,
                url=construct_url("teams", year=year, page_num=page_num, simple=simple, keys=keys),
                headers=self._headers,
            )
            return [Team(**team_data) if not isinstance(team_data, str) else team_data for team_data in response]
        else:
            return list(
                itertools.chain.from_iterable(
                    await asyncio.gather(
                        *[
                            self._get_team_page(
                                spec_num,
                                year,
                                simple,
                                keys,
                                use_caching=self.use_caching,
                                etag=self.etag,
                                silent=self.silent,
                            )
                            for spec_num in range(20)
                        ]
                    )
                )
            )

    @_caching_headers
    def districts(self, year: int) -> typing.List[District]:
        """
        Retrieves all FRC districts during a year.

        Parameters:
            year (int): An integer representing the year to retrieve its FRC districts from.

        Returns:
            typing.List[falcon_alliance.District]: A list of District objects with each object representing an active district of that year.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(current_instance=self, url=construct_url("districts", year=year), headers=self._headers)
        )
        return [District(**district_data) for district_data in response]

    @_caching_headers
    def event(self, event_key: str, simple: bool = False) -> Event:
        """
        Retrieves and returns a record of teams based on the parameters given.

        Parameters:
            event_key (str): A string representing a unique key assigned to an event to set it apart from others.
            simple (bool): A boolean that specifies whether the results for the event should be 'shortened' and only contain more relevant information.

        Returns:
            falcon_alliance.Event: An Event object representing the data given.
        """  # noqa
        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self, url=construct_url("event", key=event_key, simple=simple), headers=self._headers
            )
        )
        return Event(**response)

    @_caching_headers
    def events(
        self, year: typing.Union[range, int], simple: bool = False, keys: bool = False
    ) -> typing.List[typing.Union[Event, str]]:
        """
        Retrieves all the events from certain year(s).

        Parameters:
            year (int, range): An integer representing which year to return its events for o range object representing all the years events should be returned from.
            simple (bool): A boolean representing whether some of the information regarding an event should be stripped to only contain relevant information about the event.
            keys (bool): A boolean representing whether only the keys of the events should be returned.

        Returns:
            typing.List[typing.Union[falcon_alliance.Event, str]]: A list of Event objects representing each event in certain year(s) or a list of strings representing all the keys of the events retrieved.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

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
                    year, simple, keys, use_caching=self.use_caching, etag=self.etag, silent=self.silent
                )
            )

    @_caching_headers
    def match(
        self, match_key: str, simple: bool = False, timeseries: bool = False, zebra_motionworks: bool = False
    ) -> typing.Optional[typing.Union[typing.List[dict], Match, Match.ZebraMotionworks]]:
        """
        Retrieves information about a match.

        Per TBA, the timeseries data is in development and therefore you should NOT rely on it.

        Parameters:
            match_key (str): A string representing a unique key assigned to a match to set it apart from others.
            simple (bool): A boolean that specifies whether the results for each match should be 'shortened' and only contain more relevant information.
            timeseries (bool): A boolean that specifies whether match timeseries data should be retrieved from a match.
            zebra_motionworks (bool): A boolean that specifies whether data about where robots went during a match should be retrieved. Using this parameter, there may be no data due to the fact that very few matches use the Zebra MotionWorks technology required to get data on where the robots go during a match.

        Returns:
            typing.Optional[typing.Union[typing.List[dict], falcon_alliance.Match, falcon_alliance.Match.ZebraMotionworks]]: A Match object containing information about the match or a Match.ZebraMotionworks object representing data about where teams' robots went during the match (may not have any data for all teams or even data altogether and if so will return None) or a list of dictionaries containing timeseries data for a match.
        """  # noqa
        if (simple, timeseries, zebra_motionworks).count(True) > 1:
            raise ValueError(
                "Only one parameter out of `simple`, `keys`, and `statuses` can be True. "
                "You can't mix and match parameters."
            )

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self,
                url=construct_url(
                    "match", key=match_key, simple=simple, timeseries=timeseries, zebra_motionworks=zebra_motionworks
                ),
                headers=self._headers,
            )
        )
        if timeseries:  # pragma: no cover
            return response
        elif zebra_motionworks:
            zebra_data = response

            if zebra_data:
                return Match.ZebraMotionworks(**response)
        else:
            return Match(**response)

    @_caching_headers
    def status(self) -> APIStatus:
        """
        Retrieves information about TBA's API status.

        Returns:
            falcon_alliance.APIStatus: An APIStatus object containing information about TBA's API status.
        """
        response = InternalData.loop.run_until_complete(
            InternalData.get(current_instance=self, url=construct_url("status").rstrip("/"), headers=self._headers)
        )
        return APIStatus(**response)

    @_caching_headers
    def team(self, team_key: typing.Union[int, str], simple: bool = False) -> Team:
        """
        Retrieves and returns a record of teams based on the parameters given.

        Parameters:
            team_key (int, str): A string representing a unique key assigned to a team to set it apart from others (in the form of frcXXXX) where XXXX is the team number or an integer representing the team number of a team.
            simple (bool): A boolean that specifies whether the results for the team should be 'shortened' and only contain more relevant information.

        Returns:
            falcon_alliance.Team: A Team object representing the data given.
        """  # noqa
        team_key = to_team_key(team_key)

        response = InternalData.loop.run_until_complete(
            InternalData.get(
                current_instance=self, url=construct_url("team", key=team_key, simple=simple), headers=self._headers
            )
        )
        return Team(**response)

    @_caching_headers
    def teams(
        self, page_num: int = None, year: typing.Union[range, int] = None, simple: bool = False, keys: bool = False
    ) -> typing.List[typing.Union[Team, str]]:
        """
        Retrieves and returns a record of teams based on the parameters given.

        Parameters:
            page_num (int, optional): An integer that specifies the page number of the list of teams that should be retrieved. Teams are paginated by groups of 500, and if page_num is None, every team will be retrieved.
            year (int, range, optional): An integer that specifies if only the teams that participated during that year should be retrieved. If year is a range object, it will return all teams that participated in the years within the range object. If year isn't passed in, this method will get all teams that have ever participated in the history of FRC.
            simple (bool): A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys (bool): A boolean that specifies whether only the names of the FRC teams should be retrieved.

        Returns:
            typing.List[typing.Union[falcon_alliance.Team, str]]: A list of Team objects for each team in the list or a list of strings each representing a team's key.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        if isinstance(year, range):
            all_responses = list(
                itertools.chain.from_iterable(
                    InternalData.loop.run_until_complete(
                        asyncio.gather(
                            *[
                                self._get_team_page(
                                    page_num,
                                    spec_year,
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

            return sorted(list(set(all_responses)))

        else:
            return InternalData.loop.run_until_complete(
                self._get_team_page(
                    page_num, year, simple, keys, use_caching=self.use_caching, etag=self.etag, silent=self.silent
                )
            )
