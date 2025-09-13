def convert_to_dictionary(object_or_list: object | list[object]):
    if isinstance(object_or_list, list):
        return [vars(object_to_convert) for object_to_convert in object_or_list]

    return vars(object_or_list)
