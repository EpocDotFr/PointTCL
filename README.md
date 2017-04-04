# PointTCL

Python script that powers the [Dealabs](https://www.dealabs.com/) office [Slack](https://slack.com/) bot who talks about
[TCL](http://www.tcl.fr/) disruptions.

> TODO Screenshot

## Features

  - The bot automatically advise everyone in a specified Slack channel about disruptions
    - Which lines started or stopped to be disrupted
    - When disruption started
  - Ask the bot to check the current status of a specific line using commands (see below for more information)

## Prerequisites

  - Python 3. May eventually works with Python 2 (not tested)
  - A Slack team with an already-existing bot

## Installation

  1. Clone this repo somewhere
  2. `pip install -r requirements.txt`
  3. `python pointtcl.py initdb`

## Configuration

Copy the `.env.example` file to `.env` and fill in the configuration parameters.

Available configuration parameters are:

  - `SLACK_BOT_TOKEN` The bot API token (you can find it when editing the bot settings)
  - `SLACK_BOT_ID` You cannot find it now. Fill the other `SLACK_*` configuration paremeters, then run the `python pointtcl.py botid` command (see below for more information)
  - `SLACK_BOT_NAME` The bot username (not his name or last name!)
  - `SLACK_DISRUPTIONS_CHANNEL` The Slack channel in where to post automatic disruption messages
  - `GRANDLYON_LOGIN` Username used to login to your [data.grandlyon.com](data.grandlyon.com) account
  - `GRANDLYON_PASSWORD` Password used to login to your data.grandlyon.com account

## Usage

### Bot commands

Our bot is called `pointtcl`, but you'll obviously have to replace this name with your bot name.

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

### CLI commands

#### Get the bot ID

After defining the `SLACK_*` configuration parameters in your `.env` file, you can run this command to get your bot ID:

```
python pointtcl.py botid
```

Fill the `SLACK_BOT_ID` configuration parameter with the output.

#### (Re)Create and seed the database with every available lines

This command will wipe out the database then re-create it from scratch.

```
python pointtcl.py initdb
```

#### Connect the bot to the Slack RTM API and make him available to talk with

```
python pointtcl.py runbot
```

You'll probably need [Supervisor](http://supervisord.org/) to make him always-running.

#### Check for disruption on all lines and send message when there's one

This command also update the internal database of current disruptions.

```
python pointtcl.py checklines
```

Best usage is to create a Cron job that run it every, say, 5 minutes:

*/5 * * * * cd /path/to/pointtcl && python pointtcl.py checklines 2>&1

## How it works

> TODO
