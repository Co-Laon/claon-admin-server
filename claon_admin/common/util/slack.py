import ssl
from os import environ

import certifi
from fastapi import Request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from claon_admin.common.util.time import now
from claon_admin.config.env import config

SLACK_TOKEN = config.get("slack.token")
SLACK_CHANNEL = "#" + config.get("slack.channel")


class SlackClient:
    def __init__(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        ssl_context = ssl.create_default_context(cafile=certifi.where())

        self.client = WebClient(token=SLACK_TOKEN, ssl=ssl_context)

    def send_error_message(self, request: Request, message: str):
        text = "*CLAON ADMIN ERROR*\n" + \
               now().strftime("%Y-%m-%d %H:%M:%S") + "\n" + \
               ">*Profile*\n" + ">" + environ.get('API_ENV', '') + "\n" + \
               ">*Request URL*\n" + ">" + request.method + " " + str(request.url) + "\n" + \
               ">*Message*\n" + ">" + message

        try:
            self.client.chat_postMessage(channel=SLACK_CHANNEL, text=text)
        except SlackApiError as e:
            raise e


slack = SlackClient()
