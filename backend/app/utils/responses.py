def success_response(message: str, data: dict | list | None = None) -> dict:
    payload = {"status": "success", "message": message}
    if data is not None:
        payload["data"] = data
    return payload


def error_response(message: str, details: dict | list | str | None = None) -> dict:
    payload = {"status": "error", "message": message}
    if details is not None:
        payload["details"] = details
    return payload
