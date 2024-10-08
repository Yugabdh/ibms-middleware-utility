from typing import Union
from ibms_middleware_utility.logger_config import setup_logging

import requests
from requests.exceptions import HTTPError, Timeout, RequestException
import logging

logger = logging.getLogger(__name__)


class WebRequests:
    """
    A class to handle API requests using the requests module.

    This class supports various HTTP methods (GET, POST, PUT, DELETE, etc.),
    as well as optional authorization through Bearer tokens or API keys.
    It also supports configurable headers, query parameters, and body data.

    Attributes:
        url (str): The URL of the API endpoint.
        method (str, optional): The HTTP method to use (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        headers (dict, optional): HTTP headers to send with the request.
        params (dict, optional): Query parameters to include in the request.
        data (Union[dict, str], optional): Data to send in the body of the request for methods like POST or PUT.
        json (dict, optional): JSON data to send in the body of the request (alternative to 'data').
        auth (tuple, optional): A tuple containing the username and password for basic authentication.
        bearer_token (str, optional): Bearer token for authorization, if required.
        api_key (str, optional): API key for authorization, if required.
        timeout (Union[int, float], optional): Timeout for the request in seconds (Defaults to 30 seconds).

    Methods:
        send_request(): Sends the HTTP request using the provided parameters and handles the response.
    """

    def __init__(self, url, method='GET', headers=None, params=None, data=None, json=None,
                 auth=None, bearer_token=None, api_key=None, timeout=30):
        """
        Initializes the WebRequests class with the given parameters.

        Args:
            url (str): The API URL to send the request to.
            method (str, optional): The HTTP method to use. Defaults to 'GET'.
            headers (dict, optional): HTTP headers to include in the request. Defaults to None.
            params (dict, optional): Query parameters for the request. Defaults to None.
            data (Union[dict, str], optional): Data to be sent in the body of the request. Defaults to None.
            json (dict, optional): JSON data to be sent in the body of the request. Defaults to None.
            auth (tuple, optional): Basic auth credentials (username, password). Defaults to None.
            bearer_token (str, optional): Bearer token for authorization. Defaults to None.
            api_key (str, optional): API key for authorization. Defaults to None.
            timeout (Union[int, float], optional): Timeout for the request in seconds. Defaults to 30 seconds.
        """
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.params = params
        self.data = data
        self.json = json
        self.auth = auth
        self.timeout = timeout
        self.bearer_token = bearer_token
        self.api_key = api_key

        # Add bearer token to headers if provided
        if self.bearer_token:
            self.headers['Authorization'] = f'Bearer {self.bearer_token}'

        # Add API key to headers if provided
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key

    def send_request(self) -> Union[dict, str]:
        """
        Sends the HTTP request using the provided parameters and handles the response.

        The function supports various HTTP methods like GET, POST, PUT, DELETE, and handles
        responses with proper error checking and logging.

        Returns:
            Union[dict, str]: The response data in JSON format if available, otherwise returns the response text.

        Raises:
            HTTPError: If an HTTP error occurs (status code 4xx or 5xx).
            Timeout: If the request times out.
            RequestException: If any other request-related error occurs.
            Exception: For any other non-HTTP related exceptions.
        """
        try:
            logger.info(f"Sending {self.method} request to {self.url}")

            # Perform the HTTP request based on the method
            response = requests.request(
                method=self.method,
                url=self.url,
                headers=self.headers,
                params=self.params,
                data=self.data,
                json=self.json,
                auth=self.auth,
                timeout=self.timeout
            )

            # Raise HTTPError for bad responses (4xx and 5xx)
            response.raise_for_status()

            # Try to parse response as JSON, fallback to raw text if JSON is not available
            try:
                return response.json()
            except ValueError:
                return response.text

        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise
        except Timeout as timeout_err:
            logger.error(f"Request timed out: {timeout_err}")
            raise
        except RequestException as req_err:
            logger.error(f"Error occurred while making request: {req_err}")
            raise
        except Exception as err:
            logger.error(f"An unexpected error occurred: {err}")
            raise
