import typing

from .base_schema import BaseSchema


class ApiStatus(BaseSchema):
    """Class containing information about TBA's API status.

    Attributes:
        current_season (int): Year of the current FRC season.
        max_season (int): Maximum FRC season year for valid queries.
        is_datafeed_down (bool): True if the entire FMS API provided by FIRST is down.
        down_events (list[str]): A list of strings containing event keys of any active events that are no longer updating.
        ios (dict): App versions available for iOS (TBA).
        android (dict): App versions available for Android (TBA).
    """  # noqa

    def __init__(self, **kwargs):
        self.current_season: typing.Optional[int] = kwargs.get("current_season")
        self.max_season: typing.Optional[int] = kwargs.get("max_season")
        self.is_datafeed_down: typing.Optional[bool] = kwargs.get("is_datafeed_down")
        self.down_events: typing.Optional[list] = kwargs.get("down_events")
        self.ios: typing.Optional[dict] = kwargs.get("ios")
        self.android: typing.Optional[dict] = kwargs.get("android")

        super().__init__()
