from slackclient import SlackClient
from answers import answers
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
    database_session = None
    slack_client = None

    def __init__(self, name, token, id, available_commands=[], database_session=None):
        self.name = name
        self.token = token
        self.id = id
        self.available_commands = available_commands
        self.database_session = database_session
        self.slack_client = SlackClient(self.token)

    def get_id(self):
        bot_id = None

        result = self.slack_client.api_call('users.list')

        if result['ok']:
            users = result['members']

            for user in users:
                if 'name' in user and user['name'] == self.name:
                    bot_id = user['id']
                    break

        return bot_id

    def run(self):
        if self.slack_client.rtm_connect():
            logging.info(self.name + ' bot connected and running')

            while True:
                text, user, channel = self.parse_slack_message(self.slack_client.rtm_read())

                if text and channel:
                    try:
                        self.parse_message(text, user, channel)
                    except ValueError as ve:
                        self.say_random('empty_message', channel, user=user)
                    except NameError as ne:
                        self.say_random('invalid_command', channel, user=user)

                time.sleep(1)  # Poll for new messages every 1 second
        else:
            logging.error('Connection failed')

    def parse_slack_message(self, slack_rtm_messages):
        """Parse every incoming message and check if one or more was intented for the bot."""
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

    def say_random(self, message_id, channel, **kvargs):
        if message_id not in answers:
            logging.error('Anwser ID ' + answers + ' does\'t exists')
            return

        self.say(random.choice(answers[message_id]).format(**kvargs), channel)

    def parse_message(self, message, user, channel):
        message = re.sub('^<.*>', '', message) # Remove the mention at the beginning of the message
        message = message.strip().lower() # Remove all whitespace chars at the beginning and the end of the message and convert the case to lowercase
        message = re.sub('[' + string.punctuation + ']', '', message) # Remove all punctuation chars

        if not message:
            raise ValueError('Empty message')

        message_words = message.split()

        if len(message_words) == 0:
            raise ValueError('Empty command')

        current_command = None

        for available_command in self.available_commands:
            if message_words[0] in available_command.get_names(): # The first word is always the command name
                current_command = available_command
                break

        if not current_command:
            raise NameError('Invalid command')

        number_of_required_params = len(current_command.get_params())
        number_of_given_params = len(message_words[1:])

        if number_of_given_params < number_of_required_params:
            raise ValueError('Not enough parameters')

        params = message_words[1:number_of_required_params + 1]

        current_command.bot = self
        current_command.user = user
        current_command.channel = channel

        getattr(current_command, 'run')(*params)
