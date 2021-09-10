import time
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

    t0 = time.time()
    response = await handler(request)

    await metrics.add(
        metrics.Response(
            status=response.status,
            request_path=request.path,
            request_id=request_id,
            time_used_ms=round((time.time() - t0) * 1000)
        ),
        request.app['redis']
    )

    return response
