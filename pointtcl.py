from envparse import env, Env
from bot import *
from database import db_session, init_db
from models import *
import sys
import logging
import click
import commands
import grandlyon
import arrow


def get_bot_instance(available_commands=[]):
    return Bot(
        name=env('SLACK_BOT_NAME'),
        token=env('SLACK_BOT_TOKEN'),
        id=env('SLACK_BOT_ID'),
        available_commands=available_commands
    )


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


@cli.command()
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


@cli.command()
def check_lines():
    """Check for disruption on all lines"""
    bot = get_bot_instance()

    logging.info('Getting all current disruptions')

    grandlyon_client = grandlyon.Client(env('GRANDLYON_LOGIN'), env('GRANDLYON_PASSWORD'))

    disrupted_lines = grandlyon_client.get_disrupted_lines()

    logging.info('Got {} disrupted lines to process'.format(len(disrupted_lines)))

    logging.info('Processing new or ongoing disruptions')

    disturbed_line_ids_in_gl = []

    for disrupted_line in disrupted_lines:
        line_object = TclLine.find_line(disrupted_line)

        if not line_object:
            logging.warning('Line not found: {}'.format(disrupted_line))
            continue

        if not line_object.is_disrupted:
            logging.info('Line {} of type {} just started to get disrupted'.format(disrupted_line, line_object.type))

            line_object.is_disrupted = True
            line_object.latest_disruption_started_at = arrow.now()

            db_session.add(line_object)
        else:
            logging.info('Line {} of type {} already set as disrupted'.format(disrupted_line, line_object.type))

        disturbed_line_ids_in_gl.append(disrupted_line)

    logging.info('Processing finished disruptions')

    disturbed_line_ids_in_db = TclLine.get_disturbed_line_ids()

    finished_disruptions = list(set(disturbed_line_ids_in_db) - set(disturbed_line_ids_in_gl))

    if finished_disruptions:
        for line_name in finished_disruptions:
            line_object = TclLine.find_line(line_name)

            if not line_object:
                logging.warning('Line not found: {}'.format(line_name))
                continue

            line_object.is_disrupted = False
            line_object.latest_disruption_started_at = None

            db_session.add(line_object)
    else:
        logging.info('No finished disruption to process')

    # TODO Send updates
    # env('SLACK_DISRUPTIONS_CHANNELS')

    db_session.commit()

    logging.info('End of processing')

if __name__ == '__main__':
    cli()
