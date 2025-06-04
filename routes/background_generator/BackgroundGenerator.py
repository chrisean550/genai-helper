import azure.functions as func
import json
import os
import logging
from openai import OpenAI

CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Constants for image generation model and size
IMAGE_MODEL = "gpt-image-1"
IMAGE_SIZE = "1290x2796"


def BackgroundGenerator(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except Exception:
        body = None

    content = None
    if body and isinstance(body, dict):
        content = body.get("content")
    if not content:
        content = req.params.get("content")

    if not content:
        return func.HttpResponse(
            body=json.dumps({"message": "No content provided"}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        response = CLIENT.images.generate(
            model=IMAGE_MODEL,
            prompt=content,
            size=IMAGE_SIZE,
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return func.HttpResponse(
            body=json.dumps({"url": image_url}),
            status_code=200,
            mimetype="application/json",
        )
    except Exception as e:
        logging.exception("Failed to generate image")
        return func.HttpResponse(
            body=json.dumps({"message": "Failed to generate image"}),
            status_code=500,
            mimetype="application/json",
        )
