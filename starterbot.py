#Adopted with modifications from https://github.com/mattmakai/slack-starterbot/blob/master/starterbot.py
#Distributed under MIT license

# Run with
# export SLACK_BOT_TOKEN=thetoken
# python3 starterbot.py

import os
import time
import re
import random
from slackclient import SlackClient

import json #used for debug printing

# instantiate Slack client
token = os.environ.get('SLACK_BOT_TOKEN')
print("SLACK_BOT_TOKEN=" + token)
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
QUESTION_END = "?"
MENTION_REGEX = "^<@(.+)>(.*)" # unused? remove probably
RESPONSES = ["Absolutely.", "Probably!", "Maybe...", "Not really.", "I don't know.", "In your dreams.", "Never!", "What's the point in knowing..."]

# can simplify this function b.c. of cut functionality
def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        #uncomment line below to debug print
        print(json.dumps(event, indent = 2, sort_keys = True))
        
        if event["type"] == "message" and not "subtype" in event:
            # user_id, message = parse_direct_mention(event["text"])
            #uncomment line below to debug print
            # print(user_id, " : ", message)
            # if user_id == starterbot_id:
            return event["text"], event["channel"]
    return None, None


# unused. bah
def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Ask a questions. Questions tend to end with '"+QUESTION_END+"'. E.g., 'What is the meaning of git?' "

    # Finds and executes the given command, filling in response
    response = None

    print(command)

    # This is where you start to implement more commands!
    if command.endswith(QUESTION_END):
        response = '"' + command + '": ' + random.choice(RESPONSES);

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
    # avm: connect is designed for larger teams, 
    # see https://slackapi.github.io/python-slackclient/real_time_messaging.html
    # for details
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")