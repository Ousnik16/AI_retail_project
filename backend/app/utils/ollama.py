def ollama_api_url(base_url: str, endpoint: str) -> str:
    base = base_url.rstrip("/")
    endpoint = endpoint.lstrip("/")

    if base.endswith("/api"):
        return f"{base}/{endpoint}"

    return f"{base}/api/{endpoint}"
