from envparse import env, Env
from slackclient import SlackClient
from commands import *
from bot import *
import grandlyon
import sys
import logging
import click


@click.group()
def cli():
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        stream=sys.stdout
    )

    logging.getLogger().setLevel(logging.INFO)

    logging.info('Initializing')

    Env.read_envfile('.env')


@cli.command()
def run():
    """Run the bot himself"""
    available_commands = [
        HelpCommand(),
        MetroStatusCommand(),
        TramStatusCommand(),
        BusStatusCommand(),
        FunicularStatusCommand()
    ]

    bot = Bot(env('SLACK_BOT_NAME'), env('SLACK_BOT_TOKEN'), env('SLACK_BOT_ID'), available_commands)
    bot.run()


@cli.command()
def id():
    """Print the Slack bot ID"""
    logging.info('Getting ' + env('SLACK_BOT_NAME') + '\'s ID...')

    slack_client = SlackClient(env('SLACK_BOT_TOKEN'))

    result = slack_client.api_call('users.list')

    if result['ok']:
        users = result['members']

        for user in users:
            if 'name' in user and user['name'] == env('SLACK_BOT_NAME'):
                logging.info('Bot ID for ' + user['name'] + ' is ' + user['id'])
                break
    else:
        logging.error('Could not find bot user with the name ' + env('SLACK_BOT_NAME'))


# def get_all_tcl_lines():
#     """Download and save all existing TCL lines"""
#     grandlyon_client = grandlyon.Client(env('GRANDLYON_LOGIN'), env('GRANDLYON_PASSWORD'))
#
#     all_lines = cache.get('all_lines')
#
#     if not all_lines:
#         all_lines = {
#             'bus': [],
#             'subway_funicular': [],
#             'tram': []
#         }
#
#         bus_lines = grandlyon_client.get_all_bus_lines()
#
#         for bus_line in bus_lines:
#             if bus_line['ligne'].lower() not in all_lines['bus']:
#                 all_lines['bus'].append(bus_line['ligne'].lower())
#
#         subway_funicular_lines = grandlyon_client.get_all_subway_funicular_lines()
#
#         for subway_funicular_line in subway_funicular_lines:
#             if subway_funicular_line['ligne'].lower() not in all_lines['subway_funicular']:
#                 all_lines['subway_funicular'].append(subway_funicular_line['ligne'].lower())
#
#         tram_lines = grandlyon_client.get_all_tram_lines()
#
#         for tram_line in tram_lines:
#             if tram_line['ligne'].lower() not in all_lines['tram']:
#                 all_lines['tram'].append(tram_line['ligne'].lower())
#
#         cache.set('all_lines', all_lines)
#
#     return all_lines


if __name__ == '__main__':
    cli()
