import pytest

from ..api_client import ApiClient
from ..schemas import *
from ..utils import *


def test_event_one_argument():
    """Tests `Event` with ensuring that an instance is instantiated properly when only the key is passed in as a positional argument."""
    with ApiClient():
        chs_comp = Event("2022chcmp")
        assert chs_comp.key == "2022chcmp"


def test_event_kwarg():
    """Tests `Event` with ensuring that an instance is instantiated properly when the key is passed in as a keyword argument."""
    with ApiClient():
        chs_comp = Event(key="2022chcmp")
        assert chs_comp.key == "2022chcmp"


def test_event_alliances():
    """Tests TBA's endpoint that retrieves all alliances in an event."""
    with ApiClient():
        chs_comp_alliances = Event("2022chcmp").alliances()
        assert isinstance(chs_comp_alliances, list) and all(
            isinstance(alliance, Event.Alliance) for alliance in chs_comp_alliances
        )


def test_event_awards():
    """Tests TBA's endpoint that retrieves all awards distributed at an event."""
    with ApiClient():
        chs_comp_awards = Event("2022chcmp").awards()
        assert isinstance(chs_comp_awards, list) and all(
            isinstance(comp_award, Award) for comp_award in chs_comp_awards
        )


def test_event_district_points():
    """Tests TBA's endpoint that retrieves the district points distributed to all teams at that event."""
    with ApiClient():
        event_district_points = Event("2022chcmp").district_points()
        assert isinstance(event_district_points, Event.DistrictPoints)


def test_event_insights():
    """Tests TBA's endpoint that retrieves insights about an event."""
    with ApiClient():
        chs_comp_insights = Event("2022chcmp").insights()
        assert isinstance(chs_comp_insights, Event.Insights)


def test_event_matches():
    """Tests TBA's endpoint to retrieve all matches that occurred at an event."""
    with ApiClient():
        chs_comp_matches = Event("2022chcmp").matches()
        assert isinstance(chs_comp_matches, list) and all(
            isinstance(comp_match, Match) for comp_match in chs_comp_matches
        )


def test_event_matches_simple():
    """Tests TBA's endpoint to retrieve shortened information about all the matches that occurred at an event."""
    with ApiClient():
        chs_comp_matches = Event("2022chcmp").matches()
        chs_comp_matches_simple = Event("2022chcmp").matches(simple=True)
        assert chs_comp_matches != chs_comp_matches_simple


def test_event_matches_keys():
    """Tests TBA's endpoint to retrieve the keys of all the matches that occurred at an event."""
    with ApiClient():
        chs_comp_matches_keys = Event("2022chcmp").matches(keys=True)
        assert isinstance(chs_comp_matches_keys, list) and all(
            isinstance(match_key, str) for match_key in chs_comp_matches_keys
        )


def test_event_matches_extra_parameters():
    """Tests `Event.matches` to ensure that an error is raised when more than one parameter out of `simple`, `keys` and `timeseries` is True."""
    with pytest.raises(ValueError):
        with ApiClient():
            Event("2022chcmp").matches(simple=True, keys=True, timeseries=True)


def test_event_oprs():
    """Tests TBA's endpoint to retrieve the OPRs, DPRs, and CCWMs of all teams at an event."""
    with ApiClient():
        chs_comp_oprs = Event("2022chcmp").oprs()
        assert (
            isinstance(chs_comp_oprs, Event.OPRs)
            and isinstance(chs_comp_oprs.oprs, dict)
            and isinstance(chs_comp_oprs.dprs, dict)
            and isinstance(chs_comp_oprs.ccwms, dict)
        )


def test_event_opr_average():
    """Tests `Event.OPRs.average` to ensure that it returns the average of the OPRs of teams at an event."""
    with ApiClient():
        chs_avg_oprs = Event("2022chcmp").oprs().average()
        assert (
            isinstance(chs_avg_oprs, dict)
            and "opr" in chs_avg_oprs.keys()
            and "dpr" in chs_avg_oprs.keys()
            and "ccwm" in chs_avg_oprs.keys()
        )


def test_event_opr_average_with_metric():
    """Tests `Event.OPRs.average` with the metric argument to ensure that it only returns the metric specified."""
    with ApiClient():
        chs_avg_opr = Event("2022chcmp").oprs().average(metric="opr")
        assert isinstance(chs_avg_opr, float)


def test_event_opr_average_error():
    """Tests `Event.OPRs.average` with a wrong argument for the `metric` parameter to ensure it errors out."""
    with pytest.raises(ValueError):
        with ApiClient():
            Event("2022chcmp").oprs().average(metric="wrong metric")


def test_event_predictions():
    """Tests TBA's endpoint to retrieve the predictions for the matches at an event."""
    with ApiClient():
        chs_comp_predictions = Event("2022chcmp").predictions()
        assert isinstance(chs_comp_predictions, dict)


def test_event_rankings():
    """Tests TBA's endpoint to retrieve the rankings of all teams at an event."""
    with ApiClient():
        chs_comp_rankings = Event("2022chcmp").rankings()
        assert all(isinstance(team_key, str) for team_key in chs_comp_rankings.keys()) and all(
            isinstance(team_ranking, Event.Ranking) for team_ranking in chs_comp_rankings.values()
        )


def test_event_teams():
    """Tests TBA's endpoint to retrieve all the teams that played at an event."""
    with ApiClient():
        chs_comp_teams = Event("2022chcmp").teams()
        assert isinstance(chs_comp_teams, list) and all(isinstance(comp_team, Team) for comp_team in chs_comp_teams)


def test_event_teams_simple():
    """Tests TBA's endpoint to retrieve shortened information about all the teams that played at an event."""
    with ApiClient():
        chs_comp_teams = Event("2022chcmp").teams()
        chs_comp_teams_simple = Event("2022chcmp").teams(simple=True)
        assert chs_comp_teams != chs_comp_teams_simple


def test_event_teams_keys():
    """Tests TBA's endpoint to retrieve the keys of all the teams that played at an event.."""
    with ApiClient():
        chs_comp_teams_keys = Event("2022chcmp").teams(keys=True)
        assert isinstance(chs_comp_teams_keys, list) and all(
            isinstance(team_key, str) for team_key in chs_comp_teams_keys
        )


def test_event_teams_statuses():
    """Tests TBA's endpoint to retrieve the statuses of all the teams that played/are playing at an event.."""
    with ApiClient():
        chs_comp_teams_statuses = Event("2022chcmp").teams(statuses=True)
        assert (
            isinstance(chs_comp_teams_statuses, dict)
            and all(isinstance(team_key, str) for team_key in chs_comp_teams_statuses.keys())
            and all(isinstance(team_status, EventTeamStatus) for team_status in chs_comp_teams_statuses.values())
        )


def test_event_teams_extra_parameters():
    """Tests `Event.teams` to ensure that an error is raised when more than one parameter out of `simple`, `keys` and `statuses` is True."""
    with pytest.raises(ValueError):
        with ApiClient():
            Event("2022chcmp").teams(simple=True, keys=True, statuses=True)
