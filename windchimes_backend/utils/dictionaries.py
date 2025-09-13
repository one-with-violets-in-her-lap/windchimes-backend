from typing import Any, TypeVar
from copy import deepcopy

from windchimes_backend.utils.strings import convert_to_snake_case


DictT = TypeVar("DictT", dict[str, Any], list)


def convert_keys_to_snake_case(dictionary_or_list: DictT):
    """recursively converts dictionaries keys from CamelCase to snake_case

    Returns:
        dictionary copy with keys converted to snake_case
    """
    new_dictionary_or_list = deepcopy(dictionary_or_list)

    def convert_keys_recursively(possible_dictionary):
        if isinstance(possible_dictionary, list):
            for item in possible_dictionary:
                convert_keys_recursively(item)

            return
        elif not isinstance(possible_dictionary, dict):
            return

        for key in list(possible_dictionary.keys()):
            removed_key_value = possible_dictionary.pop(key)

            snake_case_key_name = convert_to_snake_case(key)
            possible_dictionary[snake_case_key_name] = removed_key_value

            convert_keys_recursively(removed_key_value)

    convert_keys_recursively(new_dictionary_or_list)
    return new_dictionary_or_list
