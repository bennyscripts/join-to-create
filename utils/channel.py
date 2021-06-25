import json

def get(guildId):
    return json.load(open("data/channels.json"))[str(guildId)]

def set(guildId, channelId):
    channels = json.load(open("data/channels.json"))
    channels[str(guildId)] = str(channelId)
    json.dump(channels, open('data/channels.json', 'w'))