import typing
from enum import Enum

__all__ = ["construct_url", "Metrics", "to_team_key"]


class Metrics(Enum):
    MATCH_SCORE = 1
    OPR = 2
    DPR = 3
    CCWM = 4


def construct_url(base_endpoint, **kwargs) -> str:
    """
    Constructs a URL to send a request to with the given parameters.

    Parameters:
        endpoint: The base endpoint to add all the different additions to the URL.
        kwargs: Arbritary amount of keyword arguments to construct the URL.

    Returns:
        A string of the constructed URL based on the endpoints.
    """
    return f"https://www.thebluealliance.com/api/v3/{base_endpoint}/" + "/".join(
        map(
            str,
            [
                param_name if isinstance(param_value, bool) else param_value
                for param_name, param_value in kwargs.items()
                if param_value is not None and param_value is not False
            ],
        )
    )


def to_team_key(team_number_or_key: typing.Union[int, str, "Team"]) -> str:  # noqa
    """
    Returns a team key regardless on if the parameter is the team number, the team key itself, or a Team object.

    Args:
        team_number_or_key: An integer representing a team number or a string representing the key of a team or a Team object.
    """  # noqa
    if isinstance(team_number_or_key, int):  # pragma: no cover
        return f"frc{team_number_or_key}"
    elif isinstance(team_number_or_key, str):  # pragma: no cover
        return team_number_or_key
    else:  # pragma: no cover
        return team_number_or_key.key
