import asyncio
import hashlib
import typing

import aiohttp

from .exceptions import TBAError


class InternalData:
    """Contains internal attributes such as the event loop and the client session."""

    loop = asyncio.get_event_loop()
    session = None

    @classmethod
    async def get(
        cls, *, current_instance: typing.Any, url: str, headers: dict, ssl: bool = True
    ) -> typing.Union[list, dict]:
        """
        Sends a GET request to the TBA API.

        Parameters:
            current_instance (typing.Any): The instance where the get method is being called from.
            url (str): A string representing which URL to send a GET request to.
            headers (dict): A dictionary containing the API key to authorize the request.
            ssl (bool): A boolean representing whether or not to verify the SSL certificate.

        Returns:
            An aiohttp.ClientResponse object representing the response the GET request returned.
        """

        if current_instance.etag:
            headers.update({"If-None-Match": current_instance.etag})

        async with cls.session.get(url=url, headers=headers, ssl=ssl) as response:
            response_json = await response.json()

            try:
                if current_instance.use_caching:
                    current_instance.etag = response.headers["ETag"]
            except AttributeError:  # when using a method that doesn't require requesting to TBA API.
                pass

            if isinstance(response_json, dict) and response_json.get("Error"):
                raise TBAError(response_json["Error"])
            else:
                return response_json

    @classmethod
    async def post(cls, current_instance: typing.Any, data: typing.Any, url: str) -> None:
        """
        Sends a POST request to the TBA API.

        Parameters:
            current_instance (typing.Any): The instance where the post method is being called from.
            data (str): The data to send with the POST request in JSON format as a string.
            url (str): A string representing which URL to send a POST request to.

        Returns:
            An aiohttp.ClientResponse object representing the response the POST request returned.
        """
        headers = {
            "X-TBA-Auth-Id": current_instance._auth_secret,
            "X-TBA-Auth-Sig": hashlib.md5(
                f"{current_instance._auth_secret}{url.replace('https://www.thebluealliance.com/', '')}{data}".encode(
                    "utf8"
                )
            ).hexdigest(),
        }
        async with cls.session.post(url=url, data=data, headers=headers) as response:
            if response.status != 200:
                raise TBAError((await response.json())["Error"])

    @classmethod
    async def set_session(cls) -> None:
        """Initializes a `aiohttp.ClientSession` instance to send GET/POST requests out of."""
        if cls.session is None:
            cls.session = aiohttp.ClientSession()
