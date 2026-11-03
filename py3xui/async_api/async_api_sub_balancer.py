"""This module contains the AsyncSubBalancerApi class for handling subscription balancers
in the XUI API."""

# pylint: disable=R0801
from py3xui.api.api_base import ApiFields
from py3xui.async_api.async_api_base import AsyncBaseApi
from py3xui.sub_balancer import SubBalancer


class AsyncSubBalancerApi(AsyncBaseApi):
    """This class provides methods to interact with the subscription balancers in the XUI API
    in an asynchronous way.

    Attributes and Properties:
        host (str): The XUI host URL.
        username (str): The XUI username.
        password (str): The XUI password.
        use_tls_verify (bool): Whether to verify the server TLS certificate.
        custom_certificate_path (str | None): Path to a custom certificate file.
        session (requests.Session): The session object for the API.
        max_retries (int): The maximum number of retries for the API requests.

    Public Methods:
        get_list: Retrieves a list of subscription balancers.
        add: Adds a new subscription balancer.
        update: Updates a subscription balancer.
        delete: Deletes a subscription balancer.

    Examples:
        ```python
        import py3xui

        api = py3xui.AsyncApi.from_env()
        await api.login()

        balancers: list[py3xui.SubBalancer] = await api.sub_balancer.get_list()
        ```
    """

    async def get_list(self) -> list[SubBalancer]:
        """Retrieves all subscription balancers in the subscription order.

        Returns:
            list[SubBalancer]: A list of subscription balancers.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            balancers: list[py3xui.SubBalancer] = await api.sub_balancer.get_list()
            ```
        """
        endpoint = "panel/api/sub-balancers"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Getting subscription balancers...")

        response = await self._get(url, headers)

        balancers_json = response.json().get(ApiFields.OBJ) or []
        return [SubBalancer.model_validate(data) for data in balancers_json]

    async def add(self, balancer: SubBalancer) -> SubBalancer:
        """Adds a new subscription balancer. The balancer is enabled unless `enabled` is set
        to False.

        Arguments:
            balancer (SubBalancer): The balancer to add.

        Returns:
            SubBalancer: The created balancer.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            balancer = py3xui.SubBalancer(remark="auto-fastest", inbound_ids=[1, 3])
            created: py3xui.SubBalancer = await api.sub_balancer.add(balancer)
            ```
        """
        endpoint = "panel/api/sub-balancers"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = balancer.to_form()
        self.logger.info("Adding subscription balancer: %s", balancer.remark)

        response = await self._post_form(url, headers, data)
        return SubBalancer.model_validate(response.json().get(ApiFields.OBJ))

    async def update(self, balancer_id: int, balancer: SubBalancer) -> SubBalancer:
        """Updates a subscription balancer. This is a full-row update: the strategy, the member
        weights and the sort order that are not set on `balancer` are reset to their defaults.
        Only `enabled` keeps the stored value when it was not set. To change a single field,
        get the balancer from `get_list`, modify it and pass it here.

        Arguments:
            balancer_id (int): The ID of the balancer to update.
            balancer (SubBalancer): The new state of the balancer.

        Returns:
            SubBalancer: The updated balancer.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            balancers = await api.sub_balancer.get_list()
            balancer = balancers[0]
            balancer.enabled = False
            updated: py3xui.SubBalancer = await api.sub_balancer.update(balancer.id, balancer)
            ```
        """
        endpoint = f"panel/api/sub-balancers/{balancer_id}"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        data = balancer.to_form()
        self.logger.info("Updating subscription balancer with ID: %s", balancer_id)

        response = await self._post_form(url, headers, data)
        return SubBalancer.model_validate(response.json().get(ApiFields.OBJ))

    async def delete(self, balancer_id: int) -> None:
        """Deletes a subscription balancer.

        Arguments:
            balancer_id (int): The ID of the balancer to delete.

        Examples:
            ```python
            import py3xui

            api = py3xui.AsyncApi.from_env()
            await api.login()

            await api.sub_balancer.delete(1)
            ```
        """
        endpoint = f"panel/api/sub-balancers/{balancer_id}/del"
        headers = {"Accept": "application/json"}

        url = self._url(endpoint)
        self.logger.info("Deleting subscription balancer with ID: %s", balancer_id)

        await self._post_form(url, headers, {})
        self.logger.info("Subscription balancer deleted successfully.")
