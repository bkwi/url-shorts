import json

from pydantic import BaseModel, AnyHttpUrl

from shorts.exceptions import AppException


def validate(schema):
    def decorator(func):
        async def wrapper(request):

            try:
                data = await request.json()
            except json.decoder.JSONDecodeError:
                raise AppException('Could not read request payload', 400)

            request['data'] = schema(**data)
            return await func(request)
        return wrapper
    return decorator


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
