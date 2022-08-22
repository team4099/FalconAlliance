__all__ = ["construct_url"]


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
