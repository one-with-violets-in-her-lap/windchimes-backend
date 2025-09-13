from typing import Any, Callable, Iterable, TypeVar


ItemT = TypeVar("ItemT")


def find_item(iterable: Iterable[ItemT], is_needed_item: Callable[[ItemT], bool]):
    for item in iterable:
        if is_needed_item(item):
            return item

    return None


def set_items_order(
    items: list[ItemT], keys_in_needed_order: list, get_item_key: Callable[[ItemT], Any]
):
    """reorders the list to match the order of provided keys list

    Args:
        keys_in_needed_order: list of unique keys that reference items in target list
        get_item_key: function that returns unique item key that can be matched with
            a key in `keys_in_needed_order` param
    """

    return [
        find_item(items, lambda item: get_item_key(item) == key)
        for key in keys_in_needed_order
    ]
