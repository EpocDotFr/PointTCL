from slackclient import SlackClient
import re
import string
import logging
import time
import random


__all__ = [
    'Bot'
]


class Bot:
    name = None
    token = None
    id = None

    available_commands = []
    slack_client = None

    def __init__(self, name, token, id, available_commands):
        self.name = name
        self.token = token
        self.id = id
        self.available_commands = available_commands
        self.slack_client = SlackClient(self.token)

    def run(self):
        logging.info('Connecting to Slack RTM')

        if self.slack_client.rtm_connect():
            logging.info(self.name + ' bot connected and running')

            while True:
                text, user, channel = self.parse_slack_message(self.slack_client.rtm_read())

                if text and channel:
                    try:
                        self.parse_message(text, user, channel)
                    except ValueError as ve:
                        self.say('<@' + user + '> On dirait que vous avez envoyé un message vide.', channel)
                    except NameError as ne:
                        self.say('<@' + user + '> Vous m\'avez envoyé une commande invalide.', channel)

                time.sleep(1)  # Poll for new messages every 1 second
        else:
            logging.warning('Connection failed')

    def parse_slack_message(self, slack_rtm_messages):
        """Parse every incoming message and check if one or more was intented for the bot"""
        if slack_rtm_messages and len(slack_rtm_messages) > 0:
            for message in slack_rtm_messages:
                # Make sure it was a normal text message containing the bot's name
                if message and 'text' in message and '<@' + self.id + '>' in message['text'] and 'subtype' not in message:
                    return message['text'], message['user'], message['channel']

        return None, None, None

    def say(self, text, channel):
        self.slack_client.api_call(
            'chat.postMessage',
            channel=channel,
            text=text
        )

    def parse_message(self, message, user, channel):
        message = re.sub('[' + string.punctuation + ']', '', message.strip().lower())
        message = re.sub('<.*>', '', message)

        if not message:
            raise ValueError('Empty message')

        message_words = message.split()

        if len(message_words) == 0:
            raise ValueError('Empty command')

        current_command = None

        for available_command in self.available_commands:
            if message_words[0] in available_command.get_names():
                current_command = available_command
                break

        if not current_command:
            raise NameError('Invalid command')

        number_of_required_params = len(current_command.get_params())
        number_of_given_params = len(message_words[1:])

        if number_of_given_params < number_of_required_params:
            raise ValueError('Not enough parameters')

        params = message_words[1:number_of_required_params + 1]

        current_command.slack_client = self.slack_client
        current_command.user = user
        current_command.channel = channel

        return getattr(current_command, 'run')(*params)
