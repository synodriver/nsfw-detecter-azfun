import azure.functions as func

from typing import IO
from io import BytesIO
import aiohttp
from pathlib import Path
from json import dumps

from .evaluate import evaluate_image
from .project import load_model_and_tags_from_project

model, tags = load_model_and_tags_from_project(str(Path(__file__).parent/"deepdanbooru-v4-20200814-sgd-e30"))

async def download_from_url(url: str) -> IO:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return BytesIO(await resp.read())
    except aiohttp.ClientError as e:
        print(e)

async def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "POST":
        data = req.get_body()
    else:
        url = req.params.get('url')
        if not url or len(url) == 0: url = req.params.get('pic')
        if not url or len(url) == 0: return func.HttpResponse(
                "400 BAD REQUEST: please specify an url to analyze",
                status_code=400
            )
        data = (await download_from_url(url)).getvalue()
    limit = req.params.get('limit')
    if not limit or len(limit) == 0: limit = 0.7
    else:
        try:
            limit = float(limit)
        except:
            return func.HttpResponse(
             "400 BAD REQUEST: limit is not a float number",
             status_code=400
        )
    return func.HttpResponse(dumps(evaluate_image(data, model, tags, limit)))
