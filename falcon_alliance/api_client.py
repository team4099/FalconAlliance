import asyncio
import functools
import itertools
import os
import typing
from types import TracebackType

import aiohttp
from dotenv import load_dotenv

from .schemas import *
from .utils import *

__all__ = ["ApiClient"]


class ApiClient:
    """Base class that contains all requests to the TBA API."""

    def __init__(self, api_key: str = None):
        load_dotenv()

        if api_key is None:
            try:
                api_key = os.environ["TBA_API_KEY"]
            except KeyError:  # pragma: no cover
                # If TBA_API_KEY isn't an environment variable
                api_key = os.environ["API_KEY"]

        self._headers = {"X-TBA-Auth-Key": api_key}
        BaseSchema.add_headers(self._headers)
        InternalData.loop.run_until_complete(InternalData.set_session())

    def __enter__(self) -> "ApiClient":
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[typing.Type[BaseException]],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[TracebackType],
    ) -> None:
        InternalData.loop.run_until_complete(self.close())

    # Defining across multiple files for autocomplete to work
    def synchronous(coro: typing.Coroutine) -> typing.Callable:
        """
        Decorator that wraps an asynchronous function around a synchronous function.
        Users can call the function synchronously although its internal behavior is asynchronous for efficiency.

        Parameters:
            coro: A coroutine that is passed into the decorator.

        Returns:
            A synchronous function with its internal behavior being asynchronous.
        """

        @functools.wraps(coro)
        def wrapper(self, *args, **kwargs) -> typing.Any:
            return InternalData.loop.run_until_complete(coro(self, *args, **kwargs))

        wrapper.coro = coro

        return wrapper

    async def close(self) -> None:
        """Closes the ongoing session (`aiohttp.ClientSession`)."""
        await InternalData.session.close()
        InternalData.session = aiohttp.ClientSession()

    async def _get_year_events(
        self, year: int, simple: typing.Optional[bool] = False, keys: typing.Optional[bool] = False
    ) -> typing.List[typing.Union[Event, str]]:
        """
        Retrieves all the events from a year.

        Parameters:
            year:
                An integer representing which year to return its events for.
            simple:
                A boolean representing whether some of the information regarding an event should be stripped to only contain relevant information about the event.
            keys:
                A boolean representing whether only the keys of the events should be returned.

        Returns:
            A list of Event objects representing each event in a year or a list of strings representing all the keys of the events retrieved.
        """  # noqa
        response = await InternalData.get(
            url=construct_url("events", year=year, simple=simple, keys=keys), headers=self._headers
        )
        if keys:
            return response
        else:
            return [Event(**event_data) for event_data in response]

    async def _get_team_page(
        self, page_num: int = None, year: typing.Union[range, int] = None, simple: bool = False, keys: bool = False
    ) -> typing.List[typing.Union[Team, str]]:
        """
        Returns a page of teams (a list of 500 teams or less)

        Parameters:
            page_num:
                An integer that specifies the page number of the list of teams that should be retrieved.
                Teams are paginated by groups of 500, and if page_num is None, every team will be retrieved.
            year:
                An integer that specifies if only the teams that participated during that year should be retrieved.
                If year is a range object, it will return all teams that participated in the years within the range object.
                If year is None, this method will get all teams that have ever participated in the history of FRC.
            simple:
                A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys:
                A boolean that specifies whether only the names of the FRC teams should be retrieved.

        Returns:
            A list of Team objects for each team in the list.
        """  # noqa
        response = await InternalData.get(
            url=construct_url("teams", year=year, page_num=page_num, simple=simple, keys=keys), headers=self._headers
        )
        return [Team(**team_data) if not isinstance(team_data, str) else team_data for team_data in response]

    @synchronous
    async def districts(self, year: int) -> typing.List[District]:
        """
        Retrieves all FRC districts during a year.

        Parameters:
            year:
                An integer representing the year to retrieve its FRC districts from.

        Returns:
            A list of District objects with each object representing an active district of that year.
        """
        response = await InternalData.get(url=construct_url("districts", year=year), headers=self._headers)
        return [District(**district_data) for district_data in response]

    @synchronous
    async def event(self, event_key: str, simple: typing.Optional[bool] = False) -> Event:
        """
        Retrieves and returns a record of teams based on the parameters given.

        Parameters:
            event_key:
                A string representing a unique key assigned to an event to set it apart from others.
            simple:
                A boolean that specifies whether the results for the event should be 'shortened' and only contain more relevant information.

        Returns:
            A Team object representing the data given.
        """  # noqa
        response = await InternalData.get(
            url=construct_url("event", key=event_key, simple=simple), headers=self._headers
        )
        return Event(**response)

    @synchronous
    async def events(
        self, year: typing.Union[range, int], simple: typing.Optional[bool] = False, keys: typing.Optional[bool] = False
    ) -> typing.List[typing.Union[Event, str]]:
        """
        Retrieves all the events from certain year(s).

        Parameters:
            year:
                An integer representing which year to return its events for o range object representing all the years events should be returned from.
            simple:
                A boolean representing whether some of the information regarding an event should be stripped to only contain relevant information about the event.
            keys:
                A boolean representing whether only the keys of the events should be returned.

        Returns:
            A list of Event objects representing each event in certain year(s) or a list of strings representing all the keys of the events retrieved.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        if isinstance(year, range):
            return list(
                itertools.chain.from_iterable(
                    await asyncio.gather(*[self.events.coro(self, spec_year, simple, keys) for spec_year in year])
                )
            )
        else:
            return await self._get_year_events(year, simple, keys)

    @synchronous
    async def match(
        self, match_key: str, simple: bool = False, timeseries: bool = False, zebra_motionworks: bool = False
    ) -> typing.Optional[typing.Union[typing.List[dict], Match, Match.ZebraMotionworks]]:
        """
        Retrieves information about a match.

        Per TBA, the timeseries data is in development and therefore you should NOT rely on it.

        Parameters:
            match_key:
                A string representing a unique key assigned to a match to set it apart from others.
            simple:
                A boolean that specifies whether the results for each match should be 'shortened' and only contain more relevant information.
            timeseries:
                A boolean that specifies whether match timeseries data should be retrieved from a match.
            zebra_motionworks:
                A boolean that specifies whether data about where robots went during a match should be retrieved. Using this parameter, there may be no data due to the fact that very few matches use the Zebra MotionWorks technology required to get data on where the robots go during a match.

        Returns:
            A Match object containing information about the match or a Match.ZebraMotionworks object representing data about where teams' robots went during the match (may not have any data for all teams or even data altogether and if so will return None) or a list of dictionaries containing timeseries data for a match.
        """  # noqa
        if (simple, timeseries, zebra_motionworks).count(True) > 1:
            raise ValueError(
                "Only one parameter out of `simple`, `keys`, and `statuses` can be True. "
                "You can't mix and match parameters."
            )

        response = await InternalData.get(
            url=construct_url(
                "match", key=match_key, simple=simple, timeseries=timeseries, zebra_motionworks=zebra_motionworks
            ),
            headers=self._headers,
        )
        if timeseries:  # pragma: no cover
            return response
        elif zebra_motionworks:
            zebra_data = response

            if zebra_data:
                return Match.ZebraMotionworks(**response)
        else:
            return Match(**response)

    @synchronous
    async def status(self) -> APIStatus:
        """
        Retrieves information about TBA's API status.

        Returns:
            An APIStatus object containing information about TBA's API status.
        """
        response = await InternalData.get(url=construct_url("status").rstrip("/"), headers=self._headers)
        return APIStatus(**response)

    @synchronous
    async def team(self, team_key: str, simple: bool = False) -> Team:
        """
        Retrieves and returns a record of teams based on the parameters given.

        Parameters:
            team_key:
                A string representing a unique key assigned to a team to set it apart from others (in the form of frcXXXX) where XXXX is the team number.
            simple:
                A boolean that specifies whether the results for the team should be 'shortened' and only contain more relevant information.

        Returns:
            A Team object representing the data given.
        """  # noqa
        response = await InternalData.get(url=construct_url("team", key=team_key, simple=simple), headers=self._headers)
        return Team(**response)

    @synchronous
    async def teams(
        self, page_num: int = None, year: typing.Union[range, int] = None, simple: bool = False, keys: bool = False
    ) -> typing.List[typing.Union[Team, str]]:
        """
        Retrieves and returns a record of teams based on the parameters given.

        Parameters:
            page_num:
                An integer that specifies the page number of the list of teams that should be retrieved.
                Teams are paginated by groups of 500, and if page_num is None, every team will be retrieved.
            year:
                An integer that specifies if only the teams that participated during that year should be retrieved.
                If year is a range object, it will return all teams that participated in the years within the range object.
                If year is None, this method will get all teams that have ever participated in the history of FRC.
            simple:
                A boolean that specifies whether the results for each team should be 'shortened' and only contain more relevant information.
            keys:
                A boolean that specifies whether only the names of the FRC teams should be retrieved.

        Returns:
            A list of Team objects for each team in the list.
        """  # noqa
        if simple and keys:
            raise ValueError("simple and keys cannot both be True, you must choose one mode over the other.")

        if isinstance(year, range):
            all_responses = list(
                itertools.chain.from_iterable(
                    await asyncio.gather(
                        *[self.teams.coro(self, page_num, spec_year, simple, keys) for spec_year in year]
                    )
                )
            )

            return sorted(list(set(all_responses)))

        else:
            if page_num:
                return await self._get_team_page(page_num, year, simple, keys)
            else:
                all_teams = itertools.chain.from_iterable(
                    await asyncio.gather(
                        *[self._get_team_page(page_number, year, simple, keys) for page_number in range(0, 20)]
                    )
                )
                return list(all_teams)
