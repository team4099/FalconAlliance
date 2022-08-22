import typing

from .base_schema import BaseSchema


class Media(BaseSchema):
    """Class representing most media associated with a team or event on TBA."""

    def __init__(self, **kwargs):
        self.type: typing.Optional[str] = kwargs.get("type")
        self.foreign_key: typing.Optional[str] = kwargs.get("foreign_key")

        self.details: typing.Optional[dict] = kwargs.get("details")
        self.preferred: typing.Optional[bool] = kwargs.get("preferred")

        self.direct_url: typing.Optional[str] = kwargs.get("direct_url")
        self.view_url: typing.Optional[str] = kwargs.get("view_url")

        super().__init__()
