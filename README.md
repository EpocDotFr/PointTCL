# PointTCL

Python script that powers the [Dealabs](https://www.dealabs.com/) office [Slack](https://slack.com/) bot who talks about
[TCL](http://www.tcl.fr/) disruptions.

> TODO Screenshot

## Features

  - The bot automatically advise about current disruptions:
    - Which lines started or stopped to be disrupted
    - When disruption started and stopped
    - Can post on multiple Slack channels
    - Filter on specific lines
  - Ask the bot to check the current status of a specific line using commands (see below for more information) with the same information as above

## Prerequisites

  - Python 3. May eventually works with Python 2 (not tested)
  - A Slack team with an already-existing bot

## Installation

  1. Clone this repo somewhere
  2. `pip install -r requirements.txt`
  3. `python pointtcl.py create_database`

## Configuration

Copy the `.env.example` file to `.env` and fill in the configuration parameters.

Available configuration parameters are:

  - `SLACK_BOT_TOKEN` The bot API token (you can find it when editing the bot settings)
  - `SLACK_BOT_ID` You cannot find it now. Fill the other `SLACK_*` configuration paremeters, then run the `python pointtcl.py id` command (see below for more information)
  - `SLACK_BOT_NAME` The bot username (not his name or last name!)
  - `SEND_DISRUPTION_MESSAGES_TO` A comma-separated list of Slack channel IDs in where to post automatic disruption messages. Empty to disable
  - `DISRUPTIONS_LINES` A comma-separated list of allowed TCL line names when sending automatic updates about disruptions. Empty to not filter
  - `BOT_ADMINS` A comma-separated list of Slack user IDs who can send admin commands to the bot. Empty to none
  - `GRANDLYON_LOGIN` Username used to login to your [https://data.grandlyon.com/](data.grandlyon.com) account
  - `GRANDLYON_PASSWORD` Password used to login to your data.grandlyon.com account

## Usage

### Bot commands

Our bot is called `pointtcl`, but you'll obviously have to replace this name with your own bot name.

#### Get help

> @pointtcl [aide|help|comment|dafuq|wut|hein]

#### Get a subway line status

> @pointtcl [métro|metro] {{line name}}

#### Get a tram line status

> @pointtcl tram {{line name}}

#### Get a bus line status

> @pointtcl bus {{line name}}

#### Get a funicular line status

> @pointtcl [funiculaire|funi] {{line name}}

#### Check current disruptions now (admin)

> @pointtcl [verif|vérif]

#### Reset the internal database (admin)

> @pointtcl resetbdd

### CLI commands

#### Get the bot ID

After defining the `SLACK_*` configuration parameters in your `.env` file, you can run this command to get your bot ID:

```
python pointtcl.py id
```

Fill the `SLACK_BOT_ID` configuration parameter with the output.

#### (Re)Create and seed the database with every available lines

This command will wipe out the database then re-create it from scratch.

```
python pointtcl.py create_database
```

#### Connect the bot to the Slack RTM API and make him available to talk with

```
python pointtcl.py run
```

You'll probably need [Supervisor](http://supervisord.org/) or similar to make him always-running.

#### Check for disruption on all lines and send message when there's one

This command also update the internal database of current disruptions.

```
python pointtcl.py check_lines
```

Best usage is to create a Cron job that run it every, say, 5 minutes:

```
*/5 * * * * cd /path/to/pointtcl && python pointtcl.py check_lines 2>&1
```

## How it works

> TODO
