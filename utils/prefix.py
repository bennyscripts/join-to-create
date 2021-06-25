import json

def get2(bot, message):
    return json.load(open("data/prefixes.json", "r"))[str(message.guild.id)]

def get(guildId):
    return json.load(open("data/prefixes.json", "r"))[str(guildId)]

def set(guildId, prefix):
    prefixes = json.load(open("data/prefixes.json"))
    prefixes[str(guildId)] = str(prefix)
    json.dump(prefixes, open('data/prefixes.json', 'w'))