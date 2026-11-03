"""This module contains the SubBalancer class which represents a subscription balancer
in the XUI API."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# pylint: disable=too-few-public-methods
class SubBalancerFields:
    """Stores the fields returned by the XUI API for parsing."""

    ID = "id"
    REMARK = "remark"
    STRATEGY = "strategy"
    INBOUND_IDS = "inboundIds"
    MEMBER_WEIGHTS = "memberWeights"
    SORT_ORDER = "sortOrder"
    ENABLED = "enabled"
    CREATED_AT = "createdAt"
    UPDATED_AT = "updatedAt"


class SubBalancer(BaseModel):
    """Represents a client-side balancer of the JSON subscription. The balancer appears in the
    JSON subscription of every client that sits on at least one of the selected inbounds.

    Attributes:
        remark (str): The display label, used as the config remarks. Required.
        inbound_ids (list[int]): The IDs of the member inbounds, at least one. Required.
        id (int): The ID of the balancer. Optional.
        strategy (str): The balancer strategy: "leastLoad", "leastPing", "roundRobin" or "random".
            Optional.
        member_weights (dict[int, float]): Inbound ID to weight, "leastLoad" strategy only.
            A lower weight is picked more often, absent IDs weigh 1. Optional.
        sort_order (int): The 1-based position in the subscription list. Optional.
        enabled (bool): Whether the balancer is emitted. Optional.
        created_at (int): The creation time in milliseconds. Optional.
        updated_at (int): The last update time in milliseconds. Optional.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: int = 0
    remark: str
    strategy: str = "random"
    inbound_ids: list[int] = Field(alias=SubBalancerFields.INBOUND_IDS)  # type: ignore
    member_weights: dict[int, float] = Field(  # type: ignore
        default_factory=dict, alias=SubBalancerFields.MEMBER_WEIGHTS
    )
    sort_order: int = Field(default=1, alias=SubBalancerFields.SORT_ORDER)  # type: ignore
    enabled: bool = True
    created_at: int = Field(default=0, alias=SubBalancerFields.CREATED_AT)  # type: ignore
    updated_at: int = Field(default=0, alias=SubBalancerFields.UPDATED_AT)  # type: ignore

    def to_form(self) -> dict[str, Any]:
        """Returns the form fields the panel reads when a balancer is created or updated.
        The member weights are sent as one JSON object and left out when empty. The enabled
        flag is left out unless it was set explicitly, so the panel applies its own rule:
        true on create, the stored value on update.

        Returns:
            dict[str, Any]: The form fields of the balancer.
        """
        form: dict[str, Any] = {
            SubBalancerFields.REMARK: self.remark,
            SubBalancerFields.STRATEGY: self.strategy,
            SubBalancerFields.INBOUND_IDS: self.inbound_ids,
            SubBalancerFields.SORT_ORDER: self.sort_order,
        }
        if self.member_weights:
            form[SubBalancerFields.MEMBER_WEIGHTS] = json.dumps(self.member_weights)
        if "enabled" in self.model_fields_set:
            form[SubBalancerFields.ENABLED] = self.enabled
        return form
