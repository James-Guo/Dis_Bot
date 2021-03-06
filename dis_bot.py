#!/usr/bin/python

import discord                          # wrapper for discord API
import random                           # to generate random numbers
import asyncio                          # for writing single-threaded concurrent code 
import configparser                     # reading config files

from riotwatcher import RiotWatcher
from riotwatcher import riotwatcher     # wrapper for League of Legends API
from riotwatcher import OCEANIA         # import OCEANIA region
from pprint import pprint               # for nicely formatted printing

client = discord.Client()

# discord token
global discord_token
global riot_token




def read_config():
    global discord_token, riot_token
    config = configparser.ConfigParser()
    config.readfp(open(r'config.ini'))
    discord_token = config.get('APIKeys', 'discord')
    riot_token = config.get('APIKeys', 'riot')


def get_LoL_stats(summonername):
    dict_output = {}

    # Riot API key
    watcher = RiotWatcher(riot_token, default_region=OCEANIA)

    if (watcher.can_make_request()):
        try:
            me = watcher.get_summoner(name=summonername)
        except:
            return -2

        dict_output["summonername"] = me["name"]
        dict_output["id"] = me["id"]

        # rank and divison for 5v5 solo
        try:
            rank = watcher.get_league_entry(summoner_ids=[me["id"]])
        except:
            return -1

        ranked_dic = {}

        ranked_dic["tier"] = rank[str(me["id"])][0]["tier"]
        ranked_dic["division"] = rank[str(me["id"])][0]["entries"][0]["division"]
        ranked_dic["wins"] = rank[str(me["id"])][0]["entries"][0]["wins"]
        ranked_dic["losses"] = rank[str(me["id"])][0]["entries"][0]["losses"]

        dict_output["ranked"] = ranked_dic
        # normals
        normals_dic = {}

        try:
            stats = watcher.get_stat_summary(me["id"])
        except:
            return -1
        normals_dic["wins"] = stats["playerStatSummaries"][10]["wins"]

        dict_output["normals"] = normals_dic

        return dict_output
    else:
        return -1


async def test(message):
    # for testing purposes

    author = message.author

    tmp = client.send_message(message.channel, 'Calculating messages...')
    for log in client.logs_from(message.channel, limit=100):
        if log.author == message.author:
            counter += 1
    await client.edit_message(tmp, 'You have {} messages.'.format(counter))


async def sleep(message):
    # sleep
    await asyncio.sleep(5)
    await client.send_message(message.channel, 'Done sleeping')

async def greet(message):
    # greetings
    await client.send_message(message.channel, 'Say hello')
    msg = await client.wait_for_message(author=message.author, content='hello')
    await client.send_message(message.channel, 'Hello.')


async def roll(message):
    # roll 0-100
    number = random.randint(0, 100)
    await client.send_message(message.channel, "%s: %i " % (message.author, number))



async def choose(message):
    my_string = message.content.replace("!choose ", "")
    my_list = my_string.split(",")

    await client.send_message(message.channel, random.choice(my_list))

async def join(message):
    # joining different servers
    join_link = message.content.replace("!join ", "")
    print("Join link", join_link)
    client.accept_invite(join_link)
    await client.send_message(message.channel, "Bot has joined")


async def lolstats(message):
    # for getting LoL stats
    summonername = message.content.replace("!lolstats ", "")
    summonername = message.content.replace("!lolstats", "")

    print("Summoner name ", summonername)
    stats = get_LoL_stats(summonername)

    if stats == -1:
        # Can't request from Riot API anymore
        await client.send_message(message.channel, "Wait 1 minute")
    if stats == -2:
        # Can't find summonername
        await client.send_message(message.channel, summonername + " not found")
    else:
        # Print stats
        output_string = "**Summoner:** %s\n**Rank:** %s %s\n**Wins:** %s\n**Losses:** %s" % (
            stats["summonername"], stats["ranked"]["tier"], stats["ranked"]["division"],
            stats["ranked"]["wins"], stats["ranked"]["losses"])

        output_string += "\n<http://oce.op.gg/summoner/userName=" + summonername +">"
        await client.send_message(message.channel, output_string)


async def bot_help(message):
    # for help
    output_string = ("Functions\n"
                     "**!test** - for testing purposes\n"
                     "**!lolstats** <summonername>- returns LoL stats\n"
                     "**!roll** - returns a number between 0 - 100\n"
                     "**!choose** <item1, item2, item3> - returns random item\n")
    await client.send_message(message.channel, output_string)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    ''' Action on message call '''

    # maps functions to commands
    dispatcher = {
        "test": test,
        "sleep": sleep,
        "greet": greet,
        "roll": roll,
        "choose": choose,
        "join": join,
        "lolstats": lolstats,
        "help": bot_help
    }

    if message.content.startswith("!"):
        # get the command
        command = message.content.split(' ', 1)[0]
        command = command.replace("!", "")

        # call the function
        await dispatcher[command](message)


read_config()
client.run(discord_token)