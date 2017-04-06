from envparse import env, Env
from bot import *
from database import db_session, init_db
from models import *
import sys
import logging
import click
import commands
import grandlyon


def get_bot_instance(available_commands=[]):
    return Bot(
        name=env('SLACK_BOT_NAME'),
        token=env('SLACK_BOT_TOKEN'),
        id=env('SLACK_BOT_ID'),
        available_commands=available_commands
    )


def get_human_line_type_name(type):
    if type == TclLineType.SUBWAY:
        return 'Métro'
    elif type == TclLineType.TRAM:
        return 'Tram'
    elif type == TclLineType.BUS:
        return 'Bus'
    elif type == TclLineType.FUNICULAR:
        return 'Funiculaire'
    else:
        return 'Type de ligne inconnu'


@click.group()
def cli():
    """Point TCL Slack bot"""
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
    available_commands = [getattr(commands, command)() for command in commands.__all__]

    bot = get_bot_instance(available_commands)

    logging.info('Connecting to Slack')

    bot.run()


@cli.command()
def id():
    """Print the bot ID"""
    bot = get_bot_instance()

    logging.info('Getting bot ID...')

    bot_id = bot.get_id()

    if bot_id:
        logging.info('Bot ID is ' + bot_id)
    else:
        logging.error('Could not find bot user')


def create_database():
    """Create then seed the database"""
    logging.info('Deleting and creating the database')

    init_db() # See in models.py

    grandlyon_client = grandlyon.Client(env('GRANDLYON_LOGIN'), env('GRANDLYON_PASSWORD'))

    logging.info('Seeding the database')

    logging.info('Getting all bus lines')

    # Bus lines
    bus_lines = grandlyon_client.get_all_bus_lines()
    all_bus_lines = []

    for bus_line in bus_lines:
        name = bus_line['ligne'].lower()

        if name not in all_bus_lines:
            all_bus_lines.append(name)

            db_session.add(TclLine(
                name=name,
                type=TclLineType.BUS
            ))

    db_session.commit()

    logging.info('Getting all subway and funicular lines')

    # Subway and funicular lines
    subway_funicular_lines = grandlyon_client.get_all_subway_funicular_lines()
    all_subway_funicular_lines = []

    for subway_funicular_line in subway_funicular_lines:
        name = subway_funicular_line['ligne'].lower()

        if name not in all_subway_funicular_lines:
            all_subway_funicular_lines.append(name)

            db_session.add(TclLine(
                name=name,
                type=TclLineType.FUNICULAR if name.startswith('f') else TclLineType.SUBWAY
            ))

    db_session.commit()

    logging.info('Getting all tram lines')

    # Tram lines
    tram_lines = grandlyon_client.get_all_tram_lines()
    all_tram_lines = []

    for tram_line in tram_lines:
        name = tram_line['ligne'].lower()

        if name not in all_tram_lines:
            all_tram_lines.append(name)

            db_session.add(TclLine(
                name=name,
                type=TclLineType.TRAM
            ))

    db_session.commit()

    logging.info('Done')


@cli.command(name='create_database')
def create_database_cmd():
    """Create then seed the database"""
    create_database()


def check_lines():
    """Check for disruption on all lines"""
    bot = get_bot_instance()

    logging.info('Getting all current disruptions')

    grandlyon_client = grandlyon.Client(env('GRANDLYON_LOGIN'), env('GRANDLYON_PASSWORD'))

    disrupted_lines = grandlyon_client.get_disrupted_lines()

    logging.info('Got {} disrupted lines to process'.format(len(disrupted_lines)))

    disruption_start_lines = []
    disruption_end_lines = []

    logging.info('Processing new or ongoing disruptions')

    if disrupted_lines:
        for line_name, disruption_infos in disrupted_lines.items():
            line_object = TclLine.find_line(line_name)

            if not line_object:
                logging.warning('Line not found: {}'.format(line_name))
                continue

            if not line_object.is_disrupted:
                logging.info('Line {} of type {}: start of disruption'.format(line_name, line_object.type))

                line_object.is_disrupted = True
                line_object.latest_disruption_started_at = disruption_infos['started_at']
                line_object.latest_disruption_reason = disruption_infos['reason']

                db_session.add(line_object)

                disruption_start_lines.append('*{line_type} {line_name}*{reason}'.format(
                    line_type=get_human_line_type_name(line_object.type),
                    line_name=line_name,
                    reason=' (la raison est : _' + line_object.latest_disruption_reason + '_)' if line_object.latest_disruption_reason else ''
                ))
            else:
                logging.info('Line {} of type {} already set as disrupted'.format(line_name, line_object.type))

    logging.info('Processing finished disruptions')

    disturbed_line_ids_in_db = TclLine.get_disturbed_line_ids()

    finished_disruptions = list(set(disturbed_line_ids_in_db) - set(disrupted_lines.keys()))

    if finished_disruptions:
        for line_name in finished_disruptions:
            line_object = TclLine.find_line(line_name)

            if not line_object:
                logging.warning('Line not found: {}'.format(line_name))
                continue

            logging.info('Line {} of type {}: end of disruption'.format(line_name, line_object.type))

            line_object.is_disrupted = False

            db_session.add(line_object)

            disruption_end_lines.append('*{line_type} {line_name}*{reason}'.format(
                line_type=get_human_line_type_name(line_object.type),
                line_name=line_name,
                reason=' (la raison était : _' + line_object.latest_disruption_reason + '_)' if line_object.latest_disruption_reason else ''
            ))
    else:
        logging.info('No finished disruption to process')

    recipient_channels = env.list('SLACK_DISRUPTIONS_CHANNELS', default=[])

    if recipient_channels: # If there's channels to inform
        logging.info('Sending updates to Slack')

        for recipient_channel in recipient_channels:
            if disruption_start_lines:
                bot.say_random('disruption_start', recipient_channel, lines='  - ' + '\n  - '.join(disruption_start_lines))

            if disruption_end_lines:
                bot.say_random('disruption_end', recipient_channel, lines='  - ' + '\n  - '.join(disruption_end_lines))

    db_session.commit()

    logging.info('End of processing')


@cli.command(name='check_lines')
def check_lines_cmd():
    """Check for disruption on all lines"""
    check_lines()


if __name__ == '__main__':
    cli()
