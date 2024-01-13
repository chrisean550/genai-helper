# Test locally by running "func start"

import azure.functions as func
import logging
import json
from openai import OpenAI
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# @app.route(route="ArticleSummary")
# def ArticleSummary(req: func.HttpRequest) -> func.HttpResponse:
#     logging.info('Python HTTP trigger function processed a request.')

#     name = req.params.get('name')
#     if not name:
#         try:
#             req_body = req.get_json()
#         except ValueError:
#             pass
#         else:
#             name = req_body.get('name')

#     return func.HttpResponse(
#             body = json.dumps({"text":f"{name}This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response."}),
#             status_code=200,
#             mimetype="application/json"
#     )
@app.route(route="ArticleSummary")
def ArticleSummary(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
    ]
    )

    result = completion.choices[0].message.content

    return func.HttpResponse(
            body = result,
            status_code=200,
    )