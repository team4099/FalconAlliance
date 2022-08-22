import pytest

from ..api_client import ApiClient
from ..schemas import *
from ..utils import *


def test_district_year_abbreviation():
    """Tests initializing `District` via passing in the year and then the abbreviation (eg District(2022, 'chs'))."""
    with ApiClient():
        chs_district = District(2022, "chs")
        assert chs_district.year == 2022 and chs_district.abbreviation == "chs" and chs_district.key == "2022chs"


def test_district_year_abbreviation_reversed():
    """Tests initializing `District` via passing in the abbreviation and then the year (eg District('chs', 2022))."""
    with ApiClient():
        chs_district = District("chs", 2022)
        assert chs_district.year == 2022 and chs_district.abbreviation == "chs" and chs_district.key == "2022chs"


def test_district_key():
    """Tests initializing `District` via passing in the district key (eg '2022chs')."""
    with ApiClient():
        chs_district = District("2022chs")
        assert chs_district.year == 2022 and chs_district.abbreviation == "chs" and chs_district.key == "2022chs"


def test_district_kwargs():
    """Tests initializing `District` via passing in keyword arguments."""
    with ApiClient():
        chs_district = District(key="2022chs")
        assert chs_district.year == 2022 and chs_district.abbreviation == "chs" and chs_district.key == "2022chs"


def test_district_events():
    """Tests TBA's endpoint to retrieve all events that occurred in a district."""
    with ApiClient():
        chs_events = District(2022, "chs").events()
        assert isinstance(chs_events, list) and all(isinstance(event, Event) for event in chs_events)


def test_district_events_simple():
    """Tests TBA's endpoint to retrieve shortened information about the events that occurred in a district."""
    with ApiClient():
        chs_district = District(2022, "chs")
        assert chs_district.events() != chs_district.events(simple=True)


def test_district_events_keys():
    """Tests TBA's endpoint to retrieve the keys of all the events that occurred in a district."""
    with ApiClient():
        chs_events = District(2022, "chs").events(keys=True)
        assert isinstance(chs_events, list) and all(isinstance(event_key, str) for event_key in chs_events)


def test_district_events_extra_parameters():
    """Tests `District.events` to ensure that an error is raised when `simple` and `keys` are both True."""
    with pytest.raises(ValueError):
        with ApiClient():
            District(2022, "chs").events(simple=True, keys=True)


def test_district_teams():
    """Tests TBA's endpoint to retrieve all teams that played in a district."""
    with ApiClient():
        chs_teams = District(2022, "chs").teams()
        assert isinstance(chs_teams, list) and all(isinstance(team, Team) for team in chs_teams)


def test_district_teams_simple():
    """Tests TBA's endpoint to retrieve shortened information about the teams that played in a district."""
    with ApiClient():
        chs_district = District(2022, "chs")
        assert chs_district.teams() != chs_district.teams(simple=True)


def test_district_teams_keys():
    """Tests TBA's endpoint to retrieve the keys of all the teams that played in a district."""
    with ApiClient():
        chs_teams = District(2022, "chs").teams(keys=True)
        assert isinstance(chs_teams, list) and all(isinstance(team_key, str) for team_key in chs_teams)


def test_district_teams_extra_parameters():
    """Tests `District.teams` to ensure that an error is raised when `simple` and `keys` are both True."""
    with pytest.raises(ValueError):
        with ApiClient():
            District(2022, "chs").teams(simple=True, keys=True)


def test_district_rankings():
    """Tests TBA's endpoint to retrieve the rankings of all the teams in a district."""
    with ApiClient():
        chs_rankings = District(2022, "chs").rankings()
        assert isinstance(chs_rankings, list) and all(
            isinstance(team_rank, District.Ranking) for team_rank in chs_rankings
        )
