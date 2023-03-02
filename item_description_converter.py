import json
import re

with open('lolstats/static/json/items_dd.json', 'r', encoding='utf-8') as file:
        item_dd = json.load(file)

regex = re.compile('<((?=[^bl]).*?)>')

for item in item_dd['data']:
    description = item_dd['data'][item]['description']
    description = re.sub(regex, '',description)
    description = description.replace('<lifeSteal>', '')
    item_dd['data'][item]['description'] = description

with open('lolstats/static/json/items_dd_alt.json', "w") as file:
    json.dump(item_dd, file) 