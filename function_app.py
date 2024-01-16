# Test locally by running "func start"
# import logging
# logging.info('Python HTTP trigger function processed a request.')
import azure.functions as func
from openai import OpenAI
import os
from routes.article_summary.ArticleSummarizer import ArticleSummarizer


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route(route="ArticleSummary")
def ArticleSummary(req: func.HttpRequest) -> func.HttpResponse:
    return ArticleSummarizer(req, client)