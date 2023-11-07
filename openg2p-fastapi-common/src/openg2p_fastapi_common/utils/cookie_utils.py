from starlette.responses import Response


def get_response_cookies(res: Response, name: str):
    return [
        header[1].decode().split(";", 1)[0].split("=", 1)[1]
        for header in res.raw_headers
        if header[0].decode() == "set-cookie"
        and header[1]
        and header[1].decode().lower().startswith(name.lower())
    ]
