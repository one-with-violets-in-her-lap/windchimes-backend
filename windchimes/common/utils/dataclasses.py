import dataclasses


def convert_to_dataclass(target_dict: dict, dataclass_to_convert_to):
    fields_from_dict = {
        field.name: target_dict[field.name]
        for field in dataclasses.fields(dataclass_to_convert_to)
    }

    return dataclass_to_convert_to(**fields_from_dict)
