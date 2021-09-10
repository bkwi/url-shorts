import uuid

from aiohttp import web

from shorts import metrics


@web.middleware
async def metrics_middleware(request, handler):
    request_id = uuid.uuid4().hex[:7]

    await metrics.add(
        metrics.Request(path=request.path, request_id=request_id),
        request.app['redis']
    )

    response = await handler(request)

    return response
