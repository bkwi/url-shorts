import re
import time
import uuid

import pydantic
from aiohttp import web, web_exceptions

from shorts.loggers import logger
from shorts import metrics, exceptions


@web.middleware
async def exception_middleware(request, handler):
    try:
        response = await handler(request)
    except web_exceptions.HTTPClientError as e:
        response = web.json_response({'error': e.text}, status=e.status_code)
    except pydantic.error_wrappers.ValidationError as e:
        response = web.json_response({'error': str(e)}, status=400)
    except exceptions.AppException as e:
        response = web.json_response({'error': e.message}, status=e.status_code)
    except Exception as e:
        await logger.exception(f'Unexpected error: {e}')
        response = web.json_response({'error': 'unexpected error'}, status=500)

    return response


@web.middleware
async def metrics_middleware(request, handler):
    request_id = uuid.uuid4().hex[:7]
    request['id'] = request_id

    logger.setup(request_id)
    req_path = request.path
    await logger.info(f'New request received: {request.path}')
    if re.match(r'^\/r\/\w+$', req_path):
        req_path = '/r'

    await metrics.add(
        metrics.Request(path=req_path, request_id=request_id),
        request.app['redis']
    )

    t0 = time.time()
    response = await handler(request)
    await logger.info(f'Response status code: {response.status}')

    await metrics.add(
        metrics.Response(
            status=response.status,
            request_path=req_path,
            request_id=request_id,
            time_used_ms=round((time.time() - t0) * 1000)
        ),
        request.app['redis']
    )

    return response
