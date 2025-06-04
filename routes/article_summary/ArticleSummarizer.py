import azure.functions as func
import urllib.parse
import urllib.request
import json
import os
from openai import OpenAI
import logging
import time


# Authenticate session with Open AI CLIENT
CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
REQUEST_LIMIT = 15
SUCCESS = ["completed"]
INCOMPLETE = ["queued", "in_progress", None]
FAILED = ["cancelled", "failed", "expired"]

def ArticleSummarizer(req: func.HttpRequest):
    # Getting info from the request body
    try:
        body = req.get_json()
    except:
        return func.HttpResponse(
            body = json.dumps({"message": "Dude you didn't have any json in here"}),
            status_code = 401,
            mimetype = "application/json"
        )
    
    # End the thread if param is true
    if body.get("end_thread") and validThread(body.get("thread_id")):
        return deleteThread(body.get("thread_id"))
    
    # If there is content, check if it is a part of an existing conversation
    if body.get("content"):
        if validThread(body.get("thread_id")):
            logging.info("Existing thread, continuing conversation.")
            return appendConversation(body.get("content"), body.get("thread_id"))
        else:
            logging.info("Not an existing thread. Starting new conversation.")
            return appendConversation(body.get("content"), None)
    else:
        logging.warning("no content")
        return func.HttpResponse(
            body = json.dumps({"message": "Sorry but it seems like you didn't provide any instructions"}),
            status_code = 400,
            mimetype = "application/json"
        )
    

# WARNING THIS DELETES THE THREAD SO DONT BE STUPID AND NOT KNOW WHY CONVERSATION ISNT WORKING    
# Main function for starting a conversations and returning initial summary
def appendConversation(content, thread_id) -> func.HttpResponse:
    if thread_id:
        run_res = getRunResult(continueThread(content, thread_id))
    else:
        run_res = getRunResult(initiateThread(content))

    if run_res.status in INCOMPLETE:
        logging.warning("Run timed out.")
        return func.HttpResponse(
            body = json.dumps(
                {"run_id": run_res.id,
                 "thread_id": run_res.thread_id,
                 "result": run_res,
                 "message": "Run timed out"}),
            status_code = 408,
            mimetype = "application/json"
        )
    
    if run_res.status in FAILED:
        logging.error("Run failed or expired.")
        return func.HttpResponse(
            body = json.dumps(
                {"run_id": run_res.id,
                 "thread_id": run_res.thread_id,
                 "result": run_res,
                 "message": "Run failed"}),
            status_code = 409,
            mimetype = "application/json"
        )
    
    
    logging.info("Run succeeded, getting message.")
    result = getMessage(run_res.thread_id, run_res.id)

    return func.HttpResponse(
            body = json.dumps(
                {"run_id": run_res.id,
                 "thread_id": run_res.thread_id,
                 "message": result}),
            status_code = 200,
            mimetype = "application/json"
        )

# Returns the latest message in run
def getMessage(thread_id, run_id):
    try:
        step_res = CLIENT.beta.threads.runs.steps.list(
            thread_id = thread_id,
            run_id = run_id,
            limit = 1
        )

        message_id = step_res.data[0].step_details.message_creation.message_id
        
        message_res = CLIENT.beta.threads.messages.retrieve(
            message_id = message_id,
            thread_id = thread_id
        )

        message = message_res.content[0].text.value
        return message
        
    except:
        logging.error("Issue finding message.")
        return None

# Returns if thread provided is valid
def validThread(thread_id) -> bool:
    if thread_id:
        try:
            res = CLIENT.beta.threads.retrieve(thread_id)
            return True
        except:
            logging.warning("Couldn't find requested thread.")
            return False
    return False

# Delete thread if one exist
def deleteThread(thread_id) -> func.HttpResponse:
    try:
        res = CLIENT.beta.threads.delete(thread_id)
        return func.HttpResponse(
            body = json.dumps(res),
            status_code = 200,
            mimetype = "application/json"
        )
    except:
        logging.warning("Couldn't find thread to delete. Sending success response.")
        return func.HttpResponse(
            body = json.dumps(
                {"id": thread_id,
                 "object": "thread.deleted",
                 "deleted": True}),
            status_code = 204,
            mimetype = "application/json"
        )

# Starts a new thread with content, returns run object
def initiateThread(content):
    res = CLIENT.beta.threads.create_and_run(
        assistant_id = "asst_FVSL4rY0HlkaV8PBjfuE2Xin",
        thread = {
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }
    )

    return res

# Starts a new thread with content, returns run object
def continueThread(content, thread_id):
    message = CLIENT.beta.threads.messages.create(
        thread_id = thread_id,
        role = "user",
        content = content
    )

    res = CLIENT.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = "asst_FVSL4rY0HlkaV8PBjfuE2Xin"
    )

    return res

def getRunResult(run_res):
    status = None
    notComplete = ["queued", "in_progress", None]
    attempts = 0
    run = None

    while status in notComplete and attempts < REQUEST_LIMIT:
        time.sleep(2)
        run = CLIENT.beta.threads.runs.retrieve(
            thread_id = run_res.thread_id,
            run_id = run_res.id
        )
        status = run.status
        attempts += 1
    return run
