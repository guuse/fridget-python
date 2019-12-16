def is_valid_ean(ean: str) -> bool:
    if len(ean) == 13:
        return True
    return False