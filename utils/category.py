import json

def get(guildId):
    return json.load(open("data/categories.json"))[str(guildId)]

def set(guildId, categoryId):
    categories = json.load(open("data/categories.json"))
    categories[str(guildId)] = str(categoryId)
    json.dump(categories, open('data/categories.json', 'w')) 