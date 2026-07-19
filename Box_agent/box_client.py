import os
from typing import Optional

import requests

BOX_DEVELOPER_TOKEN = os.environ.get("BOX_DEV_TOKEN")
BASE_ENDPOINT_URL = "https://api.box.com/2.0"


class BoxClientError(Exception):
    """Custom exception for BoxClient errors."""

    pass


class BoxClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {BOX_DEVELOPER_TOKEN}",
        }

    def _make_request(
        self,
        request_type: str,
        api_endpoint: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        api_url = f"{BASE_ENDPOINT_URL}/{api_endpoint}"

        if headers is None:
            headers = self.headers

        try:
            response = requests.request(
                request_type, api_url, headers=headers, params=params
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error making {request_type} request to {api_url}: {e}")
            raise BoxClientError(
                f"Failed to make {request_type} request to {api_url}"
            ) from e

        return response.json()

    def get_all_files_in_folder(self, folder_id: str) -> dict:
        api_endpoint = f"folders/{folder_id}/items"

        response = self._make_request("GET", api_endpoint)
        return response.json()

    def get_available_representations(self, file_id: str) -> dict:
        api_endpoint = f"files/{file_id}"

        params = {"fields": "representations"}

        response = self._make_request("GET", api_endpoint, params=params)

        return response.json()

    def get_extracted_text_representation_metadata(self, file_id: str) -> dict:
        api_endpoint = f"files/{file_id}"

        params = {"fields": "representations"}
        header = {**self.headers, "x-rep-hints": "[extracted_text]"}

        response = self._make_request(
            "GET", api_endpoint, headers=header, params=params
        )
        return response.json()

    def download_extracted_text_representation(self, url_template: str):
        response = self._make_request("GET", url_template, headers=self.headers)
        return response
