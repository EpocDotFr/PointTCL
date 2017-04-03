# PointTCL

Python script that powers the [Dealabs](https://www.dealabs.com/) office [Slack](https://slack.com/) bot who talks about
[TCL](http://www.tcl.fr/) disruptions, and more in the future.

> TODO Screenshot

## Features

> TODO

## Prerequisites

Python 3. May eventually works with Python 2 (not tested).

## Installation

Clone this repo, and then the usual `pip install -r requirements.txt`.

## Configuration

Copy the `.env.example` file to `.env` and fill in the configuration parameters.

Available configuration parameters are:

  - `SLACK_BOT_TOKEN` The bot API token (you can find it when editing the bot settings)
  - `SLACK_BOT_ID` You cannot find it now. Fill the other `SLACK_*` configuration paremeters, then run the `python pointtcl.py botid` command (see below for more information)
  - `SLACK_BOT_NAME` The bot name
  - `SLACK_DISCRUPTIONS_CHANNEL` The Slack channel in where to post automatic disruption messages
  - `GRANDLYON_LOGIN` Username used to login to your data.grandlyon.com account
  - `GRANDLYON_PASSWORD` Password used to login to your data.grandlyon.com account

## Usage

### Get the bot ID

After defining the available configuration values in your `.env` file, you can run this command to get your bot ID:

```
python pointtcl.py botid
```

Fill the `SLACK_BOT_ID` configuration parameter with the output.

### (Re)Create and seed the database with every available lines

```
python pointtcl.py initdb
```

### Connect the bot to the Slack RTM API and make him available to talk with

```
python pointtcl.py runbot
```

### Check for disruption on all lines and send message when there's one

```
python pointtcl.py checklines
```

This command also update the internal database of current disruptions.

## How it works

> TODO
