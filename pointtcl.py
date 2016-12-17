from envparse import env, Env
from slackclient import SlackClient
from grandlyonclient import GrandLyonClient
import sys
import logging
import click
import time
import json
import re
import random

slack_client = None
grandlyon_client = None
all_lines = None
re_words = re.compile('\w+')


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
            if message and 'text' in message and '<@' + env('SLACK_BOT_ID') + '>' in message['text'] and 'subtype' not in message:
                return message['text'], message['user'], message['channel']

    return None, None, None


def say(text, channel):
    """Make the bot say something on a channel"""
    slack_client.rtm_send_message(channel, text)


def handle_bot_mention(text, user, channel):
    """Called when a message mention the bot"""
    global all_lines

    # TODO refactor all this things to use a trigger keyword which will search for the line number
    # Trigger keywords: métro, metro, tram, bus, funiculaire, funi
    # Lines are sorted in the lines.json file

    logging.info('Mentioned: ' + text)

    words = re_words.findall(text.lower())

    target_line = [line for line in all_lines if line in words]

    count = len(target_line)

    if count == 1:
        target_line = target_line[0]

        logging.info('Getting disruptions for the line ' + target_line)

        # TODO check disturbance for this line using grandlyon_client.get_line_disruptions()
        say('<@' + user + '> ' + random.choice(['Bientôt.', 'Aucune idée pour l\'instant.']), channel)
    elif count > 1: # More than one line mentioned
        say('<@' + user + '> Hey doucement, je suis pas un robot. Une ligne à la fois SVP.', channel)
    else:
        say('<@' + user + '> ' + random.choice(['Coucou.', '_No comprendo_.', 'Ah bon ?', 'Heing ?']), channel)


@click.group()
def cli():
    """Run the script"""
    global slack_client, grandlyon_client, all_lines

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        stream=sys.stdout
    )

    logging.getLogger().setLevel(logging.INFO)

    debug('Initializing')

    Env.read_envfile('.env')

    slack_client = SlackClient(env('SLACK_BOT_TOKEN'))
    grandlyon_client = GrandLyonClient(env('GRANDLYON_LOGIN'), env('GRANDLYON_PASSWORD'))

    with open('lines.json', 'r', encoding='utf-8') as f:
        all_lines = json.load(f)

@cli.command()
def run():
    """Run the bot himself"""
    logging.info('Connecting to Slack RTM')

    if slack_client.rtm_connect():
        logging.info(env('SLACK_BOT_NAME') + ' bot connected and running')

        while True:
            text, user, channel = parse_slack_message(slack_client.rtm_read())

            if text and channel:
                handle_bot_mention(text, user, channel)

            time.sleep(1) # Poll for new messages every 1 second
    else:
        logging.critical('Connection failed')


@cli.command()
def botid():
    """Print the bot's ID"""
    logging.info('Getting ' + env('SLACK_BOT_NAME') + '\'s ID...')

    api_call = slack_client.api_call('users.list')

    if api_call['ok']:
        users = api_call['members']

        for user in users:
            if 'name' in user and user['name'] == env('SLACK_BOT_NAME'):
                logging.info('Bot ID for ' + user['name'] + ' is ' + user['id'])
    else:
        logging.critical('Could not find bot user with the name ' + env('SLACK_BOT_NAME'))


@cli.command()
def importallines():
    """Import all existing TCL lines in a JSON file"""
    global grandlyon_client

    all_lines = {
        'bus': [],
        'subway_funicular': [],
        'tram': []
    }

    logging.info('Downloading bus lines')

    bus_lines = grandlyon_client.get_all_bus_lines()

    for bus_line in bus_lines:
        if bus_line['ligne'].lower() not in all_lines['bus']:
            all_lines['bus'].append(bus_line['ligne'].lower())

    logging.info('Downloading subway and funicular lines')

    subway_funicular_lines = grandlyon_client.get_all_subway_funicular_lines()

    for subway_funicular_line in subway_funicular_lines:
        if subway_funicular_line['ligne'].lower() not in all_lines['subway_funicular']:
            all_lines['subway_funicular'].append(subway_funicular_line['ligne'].lower())

    logging.info('Downloading tram lines')

    tram_lines = grandlyon_client.get_all_tram_lines()

    for tram_line in tram_lines:
        if tram_line['ligne'].lower() not in all_lines['tram']:
            all_lines['tram'].append(tram_line['ligne'].lower())

    logging.info('Saving')

    with open('lines.json', 'w', encoding='utf-8') as f:
        json.dump(all_lines, f)


if __name__ == '__main__':
    cli()
