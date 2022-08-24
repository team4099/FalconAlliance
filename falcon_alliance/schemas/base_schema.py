class BaseSchema:
    """Base class for all schemas."""

    _headers = None

    def __init__(self):
        attributes_formatted = ""

        for attr_name, attr_value in vars(self).items():
            if attr_value is None:
                continue

            if isinstance(attr_value, dict):
                attributes_formatted += f"{attr_name}={{{'...' if attr_value else ''}}}, "
            elif isinstance(attr_value, list):
                attributes_formatted += f"{attr_name}=[{'...' if attr_value else ''}], "
            elif attr_value and type(attr_value).__name__[0].isupper():
                attributes_formatted += f"{attr_name}={type(attr_value).__name__}(...), "
            else:
                attributes_formatted += f"{attr_name}={attr_value!r}, "

        self._attributes_formatted = attributes_formatted[:-2]

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __repr__(self):  # pragma: no cover
        return f"{type(self).__name__}({self._attributes_formatted})"

    @classmethod
    def add_headers(cls, headers: dict) -> None:
        """
        Adds headers for subclasses' uses when sending requests (GET/POST).

        Args:
            headers (dict): A dictionary that is in the format of {"X-TBA-Auth-Key": api_key} for TBA be able to authorize sending requests.
        """  # noqa
        cls._headers = headers
