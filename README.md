# genai-helper

This repository contains an Azure Functions app that wraps OpenAI APIs. The project targets Python **3.12** and Functions runtime `~4`.

## Routes

- `ArticleSummary` – Summarizes an article provided in the request body.
- `BackgroundGenerator` – Generates a background image using OpenAI's `gpt-image-1` model. Supply a `content` parameter describing the desired image.

## Running Locally

Ensure the `OPENAI_API_KEY` environment variable is set and run:

```bash
func start
```
