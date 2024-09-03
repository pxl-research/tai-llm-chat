# TransformAI LLM Chat

## What's in this folder?

This repository contains a proof-of-concept Slack bot using [Azure OpenAI](https://oai.azure.com/) as the LLM's under
the hood.

## Configuration

To install the necessary libraries use `pip install -r requirements.txt`

Please create an `.env` file with the same structure as the provided `.env.example` file,
and enter your personal Azure OpenAI **api key** and **endpoint** therein,
as well as your Slack **app token** and **bot token**.

## Use

Run the python script from the terminal (or your IDE).
Add the bot to a channel or message him directly.
If configured correctly, you will be able to interact with the bot in your channels using the `/llm` command.

![slack_chat.png](../../assets/screenshots/slack_chat.png)

## Documentation

- [Create a Slack App](https://api.slack.com/apps?new_app=1)
- [Slack Bolt for Python](https://slack.dev/bolt-python/getting-started/)
- [Slack "slash" commands](https://api.slack.com/interactivity/slash-commands)
