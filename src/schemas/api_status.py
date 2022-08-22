import typing

from .base_schema import BaseSchema


class APIStatus(BaseSchema):
    """Class containing information about TBA's API status.""" ""

    def __init__(self, **kwargs):
        self.current_season: typing.Optional[int] = kwargs.get("current_season")
        self.max_season: typing.Optional[int] = kwargs.get("max_season")
        self.is_datafeed_down: typing.Optional[bool] = kwargs.get("is_datafeed_down")
        self.down_events: typing.Optional[list] = kwargs.get("down_events")
        self.ios: typing.Optional[dict] = kwargs.get("ios")
        self.android: typing.Optional[dict] = kwargs.get("android")

        super().__init__()
