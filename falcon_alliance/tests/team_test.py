import typing

import pytest

from ..api_client import ApiClient
from ..schemas import *
from ..utils import *


def test_team_frc_number():
    """Tests initializing `Team` via passing in 'frc' then the team number."""
    with ApiClient():
        team4099 = Team("frc", 4099)
        assert team4099.team_number == 4099 and team4099.key == "frc4099"


def test_team_number_frc():
    """Tests initializing `Team` via passing in the team number and then 'frc'."""
    with ApiClient():
        team4099 = Team(4099, "frc")
        assert team4099.team_number == 4099 and team4099.key == "frc4099"


def test_team_number():
    """Tests initializing `Team` via passing in the team number only."""
    with ApiClient():
        team4099 = Team(4099)
        assert team4099.team_number == 4099 and team4099.key == "frc4099"


def test_team_key():
    """Tests initializing `Team` via passing in the team key only."""
    with ApiClient():
        team4099 = Team("frc4099")
        assert team4099.team_number == 4099 and team4099.key == "frc4099"


def test_team_kwarg():
    """Tests initializing `Team` via passing in the team key only as a keyword argument."""
    with ApiClient():
        team4099 = Team(key="frc4099")
        assert team4099.key == "frc4099" and team4099.team_number == 4099


def test_team_awards():
    """Tests TBA's endpoint to retrieve all awards a team has gotten over its career."""
    with ApiClient():
        team4099_awards = Team(4099).awards()
        assert isinstance(team4099_awards, list) and all(
            isinstance(team_award, Award) for team_award in team4099_awards
        )


def test_team_awards_year():
    """Tests TBA's endpoint to retrieve all awards a team has gotten in a certain year."""
    with ApiClient():
        team4099_awards = Team(4099).awards(2022)
        assert isinstance(team4099_awards, list) and all(
            isinstance(team_award, Award) for team_award in team4099_awards
        )


def test_team_awards_range():
    """Tests `Team.awards` with passing in a range object into the `year` parameter to retrieve awards a team recieved across multiple years."""
    with ApiClient():
        team4099_awards = Team(4099).awards(range(2020, 2023))
        assert isinstance(team4099_awards, list) and all(
            isinstance(team_award, Award) for team_award in team4099_awards
        )


def test_team_years_participated():
    """Tests TBA's endpoint to retrieve all the years a team played in."""
    with ApiClient():
        team4099_years_participated = Team(4099).years_participated()
        assert isinstance(team4099_years_participated, list) and min(team4099_years_participated) == 2012


def test_team_districts():
    """Tests TBA's endpoint to retrieve all the districts the team has ever played in (eg 2020chs, 2021chs, ...)"""
    with ApiClient():
        team4099_districts = Team(4099).districts()
        assert isinstance(team4099_districts, list) and all(
            isinstance(team_district, District) for team_district in team4099_districts
        )


def test_team_matches():
    """Tests TBA's endpoint to retrieve all the matches a team played in a certain year."""
    with ApiClient():
        rapid_react_matches = Team(4099).matches(2022)
        assert isinstance(rapid_react_matches, list) and all(
            isinstance(game_match, Match) for game_match in rapid_react_matches
        )


def test_team_matches_range():
    """Tests `Team.matches` to pass in a range object for the `year` parameter to retrieve matches a team played over multiple years."""
    with ApiClient():
        team4099_matches = Team(4099).matches(range(2020, 2023))
        assert isinstance(team4099_matches, list) and all(
            isinstance(game_match, Match) for game_match in team4099_matches
        )


def test_team_matches_event_code():
    """Tests `Team.matches` to retrieve all the matches a team played in a certain event."""
    with ApiClient():
        team4099_iri_matches = Team(4099).matches(2022, "iri")
        assert isinstance(team4099_iri_matches, list) and all(
            isinstance(game_match, Match) for game_match in team4099_iri_matches
        )


def test_team_matches_event_code_keys():
    """Tests `Team.matches` to retrieve the keys of all the matches a team played in a certain event."""
    with ApiClient():
        team4099_iri_matches = Team(4099).matches(2022, "iri", keys=True)
        assert isinstance(team4099_iri_matches, list) and all(
            match_key.startswith("2022iri") for match_key in team4099_iri_matches
        )


def test_team_matches_simple():
    """Tests TBA's endpoint to retrieve shortened information about all the matches a team played in a certain year."""
    with ApiClient():
        rapid_react_matches = Team(4099).matches(2022)
        rapid_react_matches_simple = Team(4099).matches(2022, simple=True)
        assert rapid_react_matches != rapid_react_matches_simple


def test_team_matches_keys():
    """Tests TBA's endpoint to retrieve the keys of all the matches a team played in a certain year."""
    with ApiClient():
        rapid_react_matches = Team(4099).matches(2022, keys=True)
        assert isinstance(rapid_react_matches, list) and all(
            isinstance(match_key, str) for match_key in rapid_react_matches
        )


def test_team_matches_extra_parameters():
    """Tests `Team.matches` to ensure that an error is raised when simple and keys are both True.."""
    with pytest.raises(ValueError):
        with ApiClient():
            Team(4099).matches(2022, simple=True, keys=True)


def test_team_media():
    """Tests TBA's endpoint to retrieve all media a team created during a year."""
    with ApiClient():
        team4099_media = Team(4099).media(2022)
        assert isinstance(team4099_media, list) and all(isinstance(team_media, Media) for team_media in team4099_media)


def test_team_media_range():
    """Tests `Team.media` to pass in a range object in the `year` parameter to retrieve media a team made across multiple years."""
    with ApiClient():
        team4099_media = Team(4099).media(range(2019, 2023))
        assert isinstance(team4099_media, list) and all(isinstance(team_media, Media) for team_media in team4099_media)


def test_team_media_with_media_tag():
    """Tests TBA's endpoint to retrieve media a team made under a media tag."""
    with ApiClient():
        team4099_media_tag = Team(4099).media(2022, media_tag="youtube")
        assert isinstance(team4099_media_tag, list)


def test_team_robots():
    """Tests TBA's endpoint to retrive all robots a team made that were registered onto TBA."""
    with ApiClient():
        team4099_robots = Team(4099).robots()
        assert isinstance(team4099_robots, list) and all(
            isinstance(team_robot, Robot) for team_robot in team4099_robots
        )


def test_team_events():
    """Tests TBA's endpoint to retrieve all events a team has ever played at."""
    with ApiClient():
        team4099_events = Team(4099).events()
        assert isinstance(team4099_events, list) and all(
            isinstance(team_event, Event) for team_event in team4099_events
        )


def test_team_events_range():
    """Tests `Team.events` to retrieve all events a team has played at across multiple years."""
    with ApiClient():
        team4099_events = Team(4099).events(range(2020, 2023))
        assert isinstance(team4099_events, list) and all(
            isinstance(team_event, Event) for team_event in team4099_events
        )


def test_team_events_simple():
    """Tests TBA's endpoint to retrieve shortened information about all the events a team has ever played at."""
    with ApiClient():
        team4099_events = Team(4099).events(2022)
        team4099_events_simple = Team(4099).events(2022, simple=True)
        assert team4099_events != team4099_events_simple


def test_team_events_keys():
    """Tests TBA's endpoint to retrieve the keys of all the events a team has ever played at."""
    with ApiClient():
        team4099_event_keys = Team(4099).events(2022, keys=True)
        assert isinstance(team4099_event_keys, list) and all(
            isinstance(event_key, str) for event_key in team4099_event_keys
        )


def test_team_events_statuses():
    """Tests TBA's endpoint to retrieve a team's status in all the events a team has ever played at."""
    with ApiClient():
        team4099_event_statuses = Team(4099).events(2022, statuses=True)
        assert (
            isinstance(team4099_event_statuses, dict)
            and all(isinstance(event_key, str) for event_key in team4099_event_statuses.keys())
            and all(isinstance(event_status, EventTeamStatus) for event_status in team4099_event_statuses.values())
        )


@pytest.mark.parametrize(
    "year,simple,keys,statuses,match",
    (
        (None, True, True, False, "simple and keys cannot both be True"),
        (None, False, True, True, "statuses cannot be True in conjunction with simple or keys"),
        (None, False, False, True, "statuses cannot be True if a year isn't passed into Team.events."),
        (range(2020, 2023), False, False, True, "statuses cannot be True when year is a range object."),
    ),
)
def test_team_events_errors(
    year: typing.Optional[typing.Union[int, range]], simple: bool, keys: bool, statuses: bool, match: str
):
    """Tests `Team.events` to ensure an error is raised for the numerous cases that fail when entering parameters for it."""
    with pytest.raises(ValueError, match=match):
        Team(4099).events(year=year, simple=simple, keys=keys, statuses=statuses)


def test_team_event_awards():
    """Tests TBA's endpoint to retrieve all matches a team played at during an event."""
    with ApiClient():
        team4099_chcmp_awards = Team(4099).event("2022chcmp", awards=True)
        assert isinstance(team4099_chcmp_awards, list) and all(
            isinstance(chcmp_award, Award) for chcmp_award in team4099_chcmp_awards
        )


def test_team_event_matches():
    """Tests TBA's endpoint to retrieve all matches a team played at during an event."""
    with ApiClient():
        team4099_iri_matches = Team(4099).event("2022iri", matches=True)
        assert isinstance(team4099_iri_matches, list) and all(
            isinstance(iri_match, Match) for iri_match in team4099_iri_matches
        )


def test_team_event_matches_simple():
    """Tests TBA's endpoint to retrieve shortened information about all the matches a team played at during an event."""
    with ApiClient():
        team4099_iri_matches = Team(4099).event("2022iri", matches=True)
        team4099_iri_matches_simple = Team(4099).event("2022iri", matches=True, simple=True)
        assert team4099_iri_matches != team4099_iri_matches_simple


def test_team_event_matches_keys():
    """Tests TBA's endpoint to retrieve the keys of all the matches a team played at during an event."""
    with ApiClient():
        team4099_iri_matches_keys = Team(4099).event("2022iri", matches=True, keys=True)
        assert isinstance(team4099_iri_matches_keys, list) and all(
            isinstance(match_key, str) for match_key in team4099_iri_matches_keys
        )


def test_team_event_status():
    """Tests TBA's endpoint to retrieve the status of a team at an event."""
    with ApiClient():
        team4099_iri_status = Team(4099).event("2022iri", status=True)
        assert isinstance(team4099_iri_status, EventTeamStatus)


@pytest.mark.parametrize(
    "awards,matches,simple,keys,status,match",
    (
        (False, False, False, False, False, "Either awards, matches or status must be True for this function."),
        (False, True, True, True, False, "simple and keys cannot both be True"),
        (True, True, False, False, False, "awards cannot be True in conjunction with simple, keys or matches"),
        (False, True, False, False, True, "status cannot be True in conjunction with simple, keys or matches"),
    ),
)
def test_team_event_errors(awards: bool, matches: bool, simple: bool, keys: bool, status: bool, match: str):
    """Tests `Team.event` for all possible errors that could be raised from it as a result of the parameters."""
    with pytest.raises(ValueError, match=match):
        with ApiClient():
            Team(4099).event("2022iri", awards=awards, matches=matches, simple=simple, keys=keys, status=status)


def test_team_social_media():
    """Tests TBA's endpoint to retrieve all the social media accounts of a team."""
    with ApiClient():
        team4099_social_media = Team(4099).social_media()
        assert isinstance(team4099_social_media, list) and all(
            isinstance(social_media_account, Media) for social_media_account in team4099_social_media
        )


def test_team_min_match_score():
    """Tests `Team.min` to retrieve the minimum match score."""
    with ApiClient():
        minimum_match_score = Team(4099).min(2022, metric=Metrics.MATCH_SCORE)
        assert isinstance(minimum_match_score, Match) and minimum_match_score.match_number == 29


def test_team_min_oprs():
    """Tests `Team.min` to retrieve the minimum OPR/DPR/CCWM."""
    with ApiClient():
        minimum_opr, event_with_opr = Team(4099).min(2022, metric=Metrics.OPR)
        assert isinstance(minimum_opr, float) and isinstance(event_with_opr, Event)


def test_team_max_match_score():
    """Tests `Team.max` to retrieve the maximum match score."""
    with ApiClient():
        max_match_score = Team(4099).max(2022, metric=Metrics.MATCH_SCORE)
        assert isinstance(max_match_score, Match) and (
            max_match_score.comp_level == "sf" and max_match_score.match_number == 2
        )


def test_team_max_oprs():
    """Tests `Team.max` to retrieve the maximum OPR/DPR/CCWM."""
    with ApiClient():
        maximum_opr, event_with_opr = Team(4099).max(2022, metric=Metrics.OPR)
        assert isinstance(maximum_opr, float) and isinstance(event_with_opr, Event)
