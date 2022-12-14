class BaseSchema:
    """Base class for all schemas."""

    _auth_secret = ""
    _headers = None

    def __init__(self):
        attributes_formatted = ""
        self.etag = ""

        self._as_dictionary = dict(vars(self))

        for attr_name, attr_value in self._as_dictionary.items():
            if attr_value is None or attr_name.startswith("_"):  # pragma: no cover
                continue
            elif isinstance(attr_value, str) and attr_value == "" and attr_name == "etag":
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

    def __getitem__(self, item: str):
        return self._as_dictionary[item]

    def __eq__(self, other: "BaseSchema"):
        return self._as_dictionary == other._as_dictionary

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

    @classmethod
    def add_auth_secret(cls, auth_secret: str) -> None:
        """
        Adds the authentication secret for POST requests to the BaseSchema for all subclasses to access.

        Args:
            auth_secret (str): Authentication secret given by TBA for POST requests.
        """
        cls._auth_secret = auth_secret
