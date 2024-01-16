import azure.functions as func
import urllib.parse
import urllib.request
import json

def ArticleSummarizer(req: func.HttpRequest, client) -> func.HttpResponse:
    article = req.params.get('article')
    if not article:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            article = req_body.get('article')

    if article:
        contents = urllib.parse.unquote(article)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                "role": "system",
                "content": "You are an assistant with a southern accent. The user will provide you with the content from a web article. Your job is to provide a summary of the provided article. If the user has a specific question pertaining to the article you will try to find the answer using the information provided, but do not summarize the entire article."
                },
                {
                "role": "user",
                "content":f"{contents}"
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        result = completion.choices[0].message.content
        # audio = client.audio.speech.create(
        #     model = "tts-1",
        #     voice = "shimmer",
        #     input = result
        # )

        return func.HttpResponse(
            body = json.dumps({"res":f"{result}"}),
            status_code=200,
            mimetype = "application/json"
        )
    
    else:
        return func.HttpResponse(
            body = json.dumps({"res":"It seems like there is not an article included in the request."}),
            status_code=200,
            mimetype = "application/json"
        )
