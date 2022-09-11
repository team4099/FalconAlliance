import asyncio
import typing

import aiohttp

from .exceptions import TBAError


class InternalData:
    """Contains internal attributes such as the event loop and the client session."""

    loop = asyncio.get_event_loop()
    session = None

    @classmethod
    async def get(cls, *, current_instance: typing.Any, url: str, headers: dict) -> typing.Union[list, dict]:
        """
        Sends a GET request to the TBA API.

        Parameters:
            current_instance (typing.Any): The instance where the get method is being called from.
            url (str): A string representing which URL to send a GET request to.
            headers (dict): A dictionary containing the API key to authorize the request.

        Returns:
            An aiohttp.ClientResponse object representing the response the GET request returned.
        """

        if current_instance.etag:
            headers.update({"If-None-Match": current_instance.etag})

        async with cls.session.get(url=url, headers=headers) as response:
            response_json = await response.json()

            if current_instance.use_caching:
                current_instance.etag = response.headers["ETag"]

            if isinstance(response_json, dict) and response_json.get("Error"):
                raise TBAError(response_json["Error"])
            else:
                return response_json

    @classmethod
    async def set_session(cls) -> None:
        """Initializes a `aiohttp.ClientSession` instance to send GET/POST requests out of."""
        if cls.session is None:
            cls.session = aiohttp.ClientSession()
