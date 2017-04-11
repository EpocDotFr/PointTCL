from slackclient import SlackClient
from answers import answers
from database import db_session
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

    def __init__(self, name, token, id, available_commands=[]):
        self.name = name
        self.token = token
        self.id = id
        self.available_commands = available_commands
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
                    except ValueError:
                        self.say_random('empty_message', channel, user=user)
                    except NameError:
                        self.say_random('invalid_command', channel, user=user)

                time.sleep(1)  # Poll for new messages every 1 second
        else:
            logging.error('Connection failed')

    def parse_slack_message(self, slack_rtm_messages):
        """Parse every incoming message and check if one or more was intented for the bot."""
        if slack_rtm_messages and len(slack_rtm_messages) > 0:
            for message in slack_rtm_messages:
                if message and 'type' in message and message['type'] == 'message' and 'subtype' not in message:
                    if 'text' in message and message['text'].startswith('<@' + self.id + '>'):
                        return message['text'], message['user'], message['channel']

        return None, None, None

    def say(self, text, channel):
        self.slack_client.api_call(
            'chat.postMessage',
            channel=channel,
            text=text,
            as_user=True
        )

    def say_random(self, message_id, channel, **kvargs):
        if message_id not in answers:
            logging.error('Anwser ID ' + message_id + ' does\'t exists')
            return

        self.say(random.choice(answers[message_id]).format(**kvargs), channel)

    def parse_message(self, message, user, channel):
        message = re.sub('^<.*>', '', message) # Remove the mention at the beginning of the message
        message = message.strip().lower() # Remove all whitespace chars at the beginning and the end of the message and convert the case to lowercase
        message = re.sub('[' + string.punctuation + ']', '', message) # Remove all punctuation chars

        logging.info('New message: ' + message)

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
