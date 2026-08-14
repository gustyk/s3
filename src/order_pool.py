"""Waiting-order repository with identity and schema invariants."""

from __future__ import annotations

from src.models import Order

REQUIRED_FIELDS = {
    "Order ID",
    "Created Time",
    "Created Time Seconds",
    "Order List",
    "Total Item",
    "Due Time",
    "Due Time Seconds",
}


class OrderPool:
    def __init__(self, env=None) -> None:
        self.env = env
        self._change_event = env.event() if env is not None else None
        self.orders: list[Order] = []
        self.generated_order_ids: set[str] = set()
        self.generated_orders: dict[str, Order] = {}

    def _notify_change(self) -> None:
        if self.env is not None and self._change_event is not None:
            if not self._change_event.triggered:
                self._change_event.succeed()
            self._change_event = self.env.event()

    def wait_for_change(self):
        """Return an event fired by the next add/remove operation."""
        if self._change_event is None:
            raise RuntimeError("OrderPool requires an environment for event-driven waiting")
        return self._change_event

    def add_order(self, order: Order) -> None:
        missing = REQUIRED_FIELDS - order.keys()
        if missing:
            raise ValueError(f"Order is missing required fields: {sorted(missing)}")
        order_id = order["Order ID"]
        if order_id in self.generated_order_ids:
            raise ValueError(f"Duplicate Order ID: {order_id}")
        if (
            order["Created Time Seconds"] < 0
            or order["Due Time Seconds"] <= order["Created Time Seconds"]
        ):
            raise ValueError("Order timestamps must satisfy 0 <= created < due")
        if order["Total Item"] != sum(quantity for _, quantity in order["Order List"]):
            raise ValueError("Total Item does not equal order-line quantities")
        self.orders.append(order)
        self.generated_order_ids.add(order_id)
        self.generated_orders[order_id] = order
        self._notify_change()

    def remove_order(self, order_ids: str | list[str]) -> list[Order]:
        return self.remove_orders([order_ids] if isinstance(order_ids, str) else order_ids)

    def remove_orders(self, order_ids: list[str]) -> list[Order]:
        targets = set(order_ids)
        removed = [order for order in self.orders if order["Order ID"] in targets]
        self.orders = [order for order in self.orders if order["Order ID"] not in targets]
        if removed:
            self._notify_change()
        return removed

    def sort_orders(self, key: str = "Created Time", reverse: bool = False) -> list[Order]:
        numeric_keys = {"Created Time": "Created Time Seconds", "Due Time": "Due Time Seconds"}
        if key not in numeric_keys:
            raise ValueError("Sort key must be either 'Created Time' or 'Due Time'")
        self.orders.sort(key=lambda order: order[numeric_keys[key]], reverse=reverse)  # type: ignore[literal-required]
        return list(self.orders)

    def clear_orders(self) -> None:
        self.orders.clear()
        self._notify_change()

    def get_all_orders(self) -> list[Order]:
        return list(self.orders)

    def get_generated_count(self) -> int:
        return len(self.generated_order_ids)

    def get_generated_orders(self) -> list[Order]:
        return list(self.generated_orders.values())

    def get_order_count(self) -> int:
        return len(self.orders)

    def get_order_by_id(self, order_id: str) -> Order | None:
        return next((order for order in self.orders if order["Order ID"] == order_id), None)
