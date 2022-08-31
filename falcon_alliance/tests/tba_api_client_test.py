import pytest

from ..api_client import ApiClient
from ..schemas import *
from ..utils import *


def test_api_status():
    """Tests TBA's endpoint for retrieving its API status."""
    with ApiClient() as api_client:
        tba_api_status = api_client.status()
        assert isinstance(tba_api_status, APIStatus)


def test_districts():
    """Tests TBA's endpoint for retrieving all districts in a year."""
    with ApiClient() as api_client:
        all_districts = api_client.districts(year=2022)
        assert isinstance(all_districts, list) and all(isinstance(district, District) for district in all_districts)


def test_team():
    """Tests TBA's endpoint for retrieving information about a team."""
    with ApiClient() as api_client:
        team4099 = api_client.team("frc4099")
        assert team4099.team_number == 4099 and team4099.nickname == "The Falcons"


def test_team_simple():
    """Tests TBA's endpoint for retrieving shortened information about a team."""
    with ApiClient() as api_client:
        team4099 = api_client.team("frc4099")
        team4099_simple = api_client.team("frc4099", simple=True)
        assert team4099 != team4099_simple


def test_dictionary_syntax():
    """Tests a schema's "dictionary" syntax that allows you to retrieve attributes via schema["name"]"""
    with ApiClient() as api_client:
        team4099 = api_client.team("frc4099")
        assert team4099["team_number"] == 4099


def test_team_not_existing():
    """Tests `ApiClient.team` to ensure that it raises an error when you pass in an invalid team key."""
    with pytest.raises(TBAError, match="is not a valid team key"):
        with ApiClient() as api_client:
            api_client.team("frc0")


def test_event():
    """Tests TBA's endpoint for retrieving information about an event."""
    with ApiClient() as api_client:
        cmp2022 = api_client.event("2022cmptx")
        assert cmp2022.name == "Einstein Field"


def test_event_simple():
    """Tests TBA's endpoint for retrieving shortened information about an event."""
    with ApiClient() as api_client:
        cmp2022 = api_client.event("2022cmptx")
        cmp2022_simple = api_client.event("2022cmptx", simple=True)
        assert cmp2022 != cmp2022_simple


def test_event_not_existing():
    """Tests `ApiClient.event` to ensure that it raises an error when you pass in an invalid event key."""
    with pytest.raises(TBAError, match="is not a valid event key"):
        with ApiClient() as api_client:
            api_client.event(event_key="Event Doesn't Exist")


def test_events():
    """Tests TBA's endpoint for retrieving information about all the events that occurred during a year."""
    with ApiClient() as api_client:
        chs_cmp = api_client.events(year=2022)
        assert isinstance(chs_cmp, list) and all(isinstance(event, Event) for event in chs_cmp)


def test_events_range():
    """Tests the `year` parameter in `ApiClient.events` with a range object to signify that events should be retrieved from all years within the range object."""
    with ApiClient() as api_client:
        all_events = api_client.events(year=range(2020, 2023))
        assert isinstance(all_events, list) and all(isinstance(event, Event) for event in all_events)


def test_events_simple():
    """Tests TBA's endpoint for retrieving shortened information about all the events that occurred during a year."""
    with ApiClient() as api_client:
        all_events = api_client.events(year=2022)
        all_events_simple = api_client.events(year=2022, simple=True)
        assert all_events != all_events_simple


def test_events_keys():
    """Tests TBA's endpoint for retrieving the keys of all the events that occurred during a year."""
    with ApiClient() as api_client:
        all_event_keys = api_client.events(year=2022, keys=True)
        assert isinstance(all_event_keys, list) and all(isinstance(event_key, str) for event_key in all_event_keys)


def test_events_extra_parameters():
    """Tests `ApiClient.events` to ensure that an error is raised when `simple` and `keys` are both True."""
    with pytest.raises(ValueError):
        with ApiClient() as api_client:
            api_client.events(year=2022, simple=True, keys=True)


def test_match():
    """Tests TBA's endpoint for retrieving information about a match."""
    with ApiClient() as api_client:
        einstein_final = api_client.match("2022cmptx_f1m1")
        assert einstein_final.alliances["red"].score == 126 and einstein_final.alliances["blue"].score == 127


def test_match_simple():
    """Tests TBA's endpoint for retrieving shortened information about a match."""
    with ApiClient() as api_client:
        einstein_final = api_client.match("2022cmptx_f1m1")
        einstein_final_simple = api_client.match("2022cmptx_f1m1", simple=True)
        assert einstein_final != einstein_final_simple


def test_match_timeseries():
    """Tests `TBAError` being raised for timeseries data regarding an invalid endpoint since timeseries data isn't implemented yet for many matches."""
    with pytest.raises(TBAError, match="Invalid endpoint"):
        with ApiClient() as api_client:
            api_client.match("2022cmptx_f1m1", timeseries=True)


def test_match_zebra_motionworks():
    """Tests TBA's endpoint for retrieving Zebra MotionWorks data from a match."""
    with ApiClient() as api_client:
        einstein_zebra = api_client.match("2022cmptx_f1m1", zebra_motionworks=True)
        assert (
            isinstance(einstein_zebra, Match.ZebraMotionworks)
            and all(isinstance(team, Match.ZebraMotionworks.Team) for team in einstein_zebra.alliances["red"])
            and all(isinstance(team, Match.ZebraMotionworks.Team) for team in einstein_zebra.alliances["blue"])
        )


def test_match_extra_parameters():
    """Tests `ApiClient.events` to ensure that an error is raised when more than one parameter out of `simple`, `zebra_motionworks` and `timeseries` are True."""
    with pytest.raises(ValueError):
        with ApiClient() as api_client:
            api_client.match("2022cmptx_f1m1", simple=True, timeseries=True, zebra_motionworks=True)


def test_teams():
    """Tests TBA's endpoint for retrieving information about all the teams that played during a year."""
    with ApiClient() as api_client:
        all_teams = api_client.teams(page_num=1, year=2022)
        assert isinstance(all_teams, list) and all(isinstance(team, Team) for team in all_teams)


def test_teams_without_page_num():
    """Tests `ApiClient.teams` with finding all teams that played during a season and not just one page (500 teams)."""
    with ApiClient() as api_client:
        all_teams = api_client.teams(year=2022)
        assert isinstance(all_teams, list) and all(isinstance(team, Team) for team in all_teams)


def test_teams_range():
    """Tests TBA's endpoint for retrieving information about all the teams that played across numerous years via passing in a range object into the `year` parameter."""
    with ApiClient() as api_client:
        all_range_teams = api_client.teams(page_num=1, year=range(2020, 2023))
        assert (
            isinstance(all_range_teams, list)
            and all(isinstance(team, Team) for team in all_range_teams)
            and not set(all_range_teams).difference(all_range_teams)
        )


def test_teams_simple():
    """Tests TBA's endpoint for retrieving shortened information about all the teams that played during a year."""
    with ApiClient() as api_client:
        all_teams = api_client.teams(page_num=1, year=2022)
        all_teams_simple = api_client.teams(page_num=1, year=2022, simple=True)
        assert all_teams != all_teams_simple


def test_teams_keys():
    """Tests TBA's endpoint for retrieving the keys of all the teams that played during a year."""
    with ApiClient() as api_client:
        all_team_keys = api_client.teams(page_num=1, year=2022, keys=True)
        assert isinstance(all_team_keys, list) and all(isinstance(team_key, str) for team_key in all_team_keys)


def test_teams_extra_parameters():
    """Tests `ApiClient.teams` to ensure that an error is raised when `simple` and `keys` are both True."""
    with pytest.raises(ValueError):
        with ApiClient() as api_client:
            api_client.teams(page_num=1, year=2022, simple=True, keys=True)
