import pytest

from ..api_client import ApiClient
from ..utils import *
from ..schemas import *


def test_event_one_argument():
    """Tests `Event` with ensuring that an instance is instantiated properly when only the key is passed in as a positional argument."""
    with ApiClient():
        chs_comp = Event("2022chcmp")
        assert chs_comp.key == "2022chcmp"


def test_event_two_arguments():
    """Tests `Event` with ensuring that an instance is instantiated properly when the year and then the event code are passed in as positional arguments."""
    with ApiClient():
        chs_comp = Event(2022, "chcmp")
        assert chs_comp.key == "2022chcmp" and chs_comp.year == 2022 and chs_comp.event_code == "chcmp"


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


def test_event_min_match_score():
    """Tests `Event.min` to retrieve the minimum match score during an event."""
    with ApiClient():
        minimum_match_score = Event("2022chcmp").min(metric=Metrics.MATCH_SCORE)
        assert isinstance(minimum_match_score, Match)


def test_team_min_opr():
    """Tests `Event.min` to retrieve the minimum OPR/DPR/CCWM during an event."""
    with ApiClient():
        minimum_opr, team = Event("2022chcmp").min(metric=Metrics.OPR)
        assert isinstance(minimum_opr, float) and isinstance(team, Team)


def test_event_max_match_score():
    """Tests `Event.max` to retrieve the maximum match score during an event."""
    with ApiClient():
        maximum_match_score = Event("2022chcmp").max(metric=Metrics.MATCH_SCORE)
        assert isinstance(maximum_match_score, Match)


def test_event_max_opr():
    """Tests `Event.max` to retrieve the maximum OPR/DPR/CCWM during an event."""
    with ApiClient():
        maximum_opr, team = Event("2022chcmp").max(metric=Metrics.OPR)
        assert isinstance(maximum_opr, float) and isinstance(team, Team)


def test_event_average_match_score():
    """Tests `Event.average` to retrieve the average match score during an event."""
    with ApiClient():
        average_match_score = Event("2022chcmp").average(metric=Metrics.MATCH_SCORE)
        assert isinstance(average_match_score, float)


def test_event_average_opr():
    """Tests `Event.average` to retrieve the average OPR during an event."""
    with ApiClient():
        average_opr = Event("2022chcmp").average(metric=Metrics.OPR)
        assert isinstance(average_opr, float)


def test_update_event_info():
    """Mock test for `Event.update_info` which passes in data and expects back an error about a wrong key."""
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").update_info({"fake": "data"})


def test_update_alliance_selections():
    """Mock test for `Event.update_alliance_selections` which passes in data and expects back an error about a wrong key."""  # noqa
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").update_alliance_selections([["not a real team", "frc120000"], ["foo bar"]])


def test_update_awards():
    """Mock test for `Event.update_awards` which passes in data and expects back an error about a wrong key."""
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").update_awards([{"fake": "award"}])


def test_update_matches():
    """Mock test for `Event.update_matches` which passes in data and expects back an error about a wrong key."""
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").update_matches([{"qm1000": "match"}])


def test_delete_matches():
    """Mock test for `Event.delete_matches` which passes in data and expects back an error about a wrong key."""
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").delete_matches(["qm100"])


def test_update_team_list():
    """Mock test for `Event.update_team_list` which passes in data and expects back an error about a wrong key."""
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").update_team_list(["frc1000000", "frc0"])


def test_update_match_videos():
    """Mock test for `Event.update_match_videos` which passes in data and expects back an error about a wrong key."""
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").update_match_videos({"qm0": "yt-link"})


def test_update_media():
    """Mock test for `Event.update_media` which passes in data and expects back an error about a wrong key."""
    with pytest.raises(TBAError, match="X-TBA-Auth-Sig"):
        with ApiClient(auth_secret="NOT A REAL AUTH SECRET"):
            Event("2022chcmp").update_media(["yt-video-1"])
