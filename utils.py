def dynamodb_to_dict (attrs: dict) -> dict:
    """
    Convert dynamodb attributes to python dictionary
    by flatterning the nested dictory
    """
    di = {}
    for key, val in attrs.items():
        di[key] = next(iter(val.values()))
    return di