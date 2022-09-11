class NotModifiedSinceError(Exception):
    """Error raised when the content of the response hasn't been modified (utilized when `use_caching` is True or `etag` isn't an empty string."""  # noqa


class TBAError(Exception):
    """Error raised when TBA returns an error from its end when requesting to its API."""
