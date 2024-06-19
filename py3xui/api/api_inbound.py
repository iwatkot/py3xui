from typing import Any

from py3xui.api.api_base import ApiFields, BaseApi
from py3xui.inbound import Inbound
from py3xui.utils import Logger

logger = Logger(__name__)


class InboundApi(BaseApi):
    def get_list(self) -> list[Inbound]:
        endpoint = "panel/api/inbounds/list"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Getting inbounds...")

        response = self._get(url, headers)

        inbounds_json = response.json().get(ApiFields.OBJ)
        inbounds = [Inbound.model_validate(data) for data in inbounds_json]
        return inbounds

    def add(self, inbound: Inbound) -> None:
        endpoint = "panel/api/inbounds/add"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        logger.info("Adding inbound: %s", inbound)

        self._post(url, headers, data)
        logger.info("Inbound added successfully.")

    def delete(self, inbound_id: int) -> None:
        endpoint = f"panel/api/inbounds/del/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}

        logger.info("Deleting inbound with ID: %s", inbound_id)
        self._post(url, headers, data)
        logger.info("Inbound deleted successfully.")

    def update(self, inbound_id: int, inbound: Inbound) -> None:
        endpoint = f"panel/api/inbounds/update/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = inbound.to_json()
        logger.info("Updating inbound: %s", inbound)

        self._post(url, headers, data)
        logger.info("Inbound updated successfully.")

    def reset_stats(self) -> None:
        endpoint = "panel/api/inbounds/resetAllTraffics"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Resetting inbounds stats...")

        self._post(url, headers, data)
        logger.info("Inbounds stats reset successfully.")

    def reset_client_stats(self, inbound_id: int) -> None:
        endpoint = f"panel/api/inbounds/resetAllClientTraffics/{inbound_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data: dict[str, Any] = {}
        logger.info("Resetting inbound client stats for ID: %s", inbound_id)

        self._post(url, headers, data)
        logger.info("Inbound client stats reset successfully.")
