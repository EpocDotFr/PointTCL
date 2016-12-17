from envparse import env, Env
import slackclient
import sys
import logging
import click
import time

slack_client = None


def debug(message, err=False, terminate=False):
    """Log a regular or error message to the standard output, optionally terminating the script."""
    logging.getLogger().log(logging.ERROR if err else logging.INFO, message)

    if terminate:
        sys.exit(1)


def parse_slack_message(slack_rtm_messages):
    """Parse every message and check if one or more was intented for the bot"""
    if slack_rtm_messages and len(slack_rtm_messages) > 0:
        for message in slack_rtm_messages:
            # Make sure it was a normal text message containing the bot's name
            if message and message['type'] == 'message' and '<@' + env('SLACK_BOT_ID') + '>' in message['text'] and 'subtype' not in message:
                return message['text'], message['channel']

    return None, None


def say(text, channel):
    """Make the bot say something on a channel"""
    slack_client.api_call('chat.postMessage', channel=channel, text=text, as_user=True) # TODO Maybe use the RPM API?


def handle_bot_mention(text, channel):
    """Called when a message mention the bot"""
    if channel != 'testbotpointtcl':
        say('Désoley, je sais rien faire pour le moment. Mon supérieur @maxime est en train de me former.', channel)


@click.group()
def cli():
    """Run the script"""
    global slack_client

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        stream=sys.stdout
    )

    logging.getLogger().setLevel(logging.INFO)

    debug('Initializing')

    Env.read_envfile('.env')

    slack_client = slackclient.SlackClient(env('SLACK_BOT_TOKEN'))


@cli.command()
def run():
    """Run the Point TCL Slack bot"""
    if slack_client.rtm_connect():
        logging.info(env('SLACK_BOT_NAME') + ' bot connected and running')

        while True:
            text, channel = parse_slack_message(slack_client.rtm_read())

            if text and channel:
                handle_bot_mention(text, channel)

            time.sleep(1) # Poll every 1 second
    else:
        logging.critical('Connection failed. Invalid Slack token or bot ID?')


@cli.command()
def botid():
    """Print the Point TCL Slack bot ID"""
    api_call = slack_client.api_call('users.list')

    if api_call.get('ok'):
        users = api_call.get('members')

        for user in users:
            if 'name' in user and user.get('name') == env('SLACK_BOT_NAME'):
                logging.info('Bot ID for ' + user['name'] + ' is ' + user.get('id'))
    else:
        logging.critical('Could not find bot user with the name ' + env('SLACK_BOT_NAME'))


if __name__ == '__main__':
    cli()
