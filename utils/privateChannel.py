import json

def add(ownerId, channelId, private: bool):
    privateChannels = json.load(open("data/privateChannels.json"))
    privateChannels[str(ownerId)] = {}
    privateChannels[str(ownerId)]["channelId"] = str(channelId)
    privateChannels[str(ownerId)]["private"] = bool(private)
    json.dump(privateChannels, open('data/privateChannels.json', 'w'))    

def remove(ownerId):
    privateChannels = json.load(open("data/privateChannels.json"))
    privateChannels.pop(str(ownerId), True)
    json.dump(privateChannels, open('data/privateChannels.json', 'w'))   

def get(ownerId = None):
    if ownerId is not None:
        return json.load(open("data/privateChannels.json"))[str(ownerId)]

    else:
        return json.load(open("data/privateChannels.json"))