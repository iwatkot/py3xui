from py3xui.api.api_base import BaseApi
from py3xui.utils import Logger

logger = Logger(__name__)


class DatabaseApi(BaseApi):
    def export(self) -> None:
        endpoint = "panel/api/inbounds/createbackup"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        logger.info("Exporting database...")

        self._get(url, headers, skip_check=True)
        logger.info("Database exported successfully.")
