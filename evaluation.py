import json
import pandas as pd
from pprint import pprint

with open('res.json', 'r') as f:
    pprint(pd.read_json(json.dumps(json.load(f)), orient='records'))


with open('pretty.json', 'r') as handle:
    data = json.load(handle)

