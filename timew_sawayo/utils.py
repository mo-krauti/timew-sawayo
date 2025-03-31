def check_optional_key_val_in_nested_dict(data: dict, key_path: list[str], value) -> bool:
    """Check if key_path exists in nested dict and element at key_path is value"""
    cur_element = data
    for key in key_path:
        if cur_element is None:
            return False
        if key in cur_element:
            cur_element = cur_element[key]
        else:
            return False
    return cur_element == value


def exit_with_msg(msg: str, error=False):
    print(msg)
    exit(error)
