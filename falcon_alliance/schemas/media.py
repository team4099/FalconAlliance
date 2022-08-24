import typing

from .base_schema import BaseSchema


class Media(BaseSchema):
    """Class representing most media associated with a team or event on TBA.

    Attributes:
        type (str, optional): String type of the media element.
        foreign_key (str): The key used to identify this media on the media site.
        details (dict, optional): If required, a JSON dict of additional media information.
        preferred (bool, optional): True if the media is of high quality.
        direct_url (str, optional): Direct URL to the media.
        view_url (str, optional): The URL that leads to the full web page for the media, if one exists.
    """

    def __init__(self, **kwargs):
        self.type: typing.Optional[str] = kwargs.get("type")
        self.foreign_key: typing.Optional[str] = kwargs.get("foreign_key")

        self.details: typing.Optional[dict] = kwargs.get("details")
        self.preferred: typing.Optional[bool] = kwargs.get("preferred")

        self.direct_url: typing.Optional[str] = kwargs.get("direct_url")
        self.view_url: typing.Optional[str] = kwargs.get("view_url")

        super().__init__()
