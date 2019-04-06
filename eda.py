import pandas as pd
import urllib.request
import simplejson

df = pd.read_csv('salary.csv')
"""
df_case = df.groupby(['LOCATION', "CASE STATUS"]).size().reset_index(name='counts')
df_case.to_csv('case_status.csv', index=False)
"""

url = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=1000-largest-us-cities-by-population-with-geographic-coordinates&rows=1000&sort=-rank&facet=city&facet=state"
coord_json = simplejson.load(urllib.request.urlopen(url))

# Get the first row
# print(coord_json['records'][0]['fields'])
rows = coord_json['records']
coord_raw = []
for row in rows:
	content = row['fields']
	coord_raw.append([content['city'],content['state'],
		             content['coordinates'][0],content['coordinates'][1]])

coord = pd.DataFrame(coord_raw, columns=['city','state','latitude','longitude'])
coord['city'] = coord['city'].str.upper()
print(coord)

df['CITY'], df['STATE'] = df.LOCATION.str.split(', ', 1).str

state = pd.read_csv('state.csv').values
state_dict = dict()
for i in state:
	state_dict[i[0]] =i[1]

df['STATE'].replace(state_dict)

df = df.merge(coord,how='left', left_on='CITY', right_on='city')
df.to_csv('new_df.csv')
