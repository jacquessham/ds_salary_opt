import pandas as pd
import urllib.request
import requests
import simplejson
import plotly
import plotly.graph_objs as go
from plotly.offline import *
from bs4 import BeautifulSoup

# To initiate ploty to run offline
init_notebook_mode(connected=True)


# Request the html file and extract the raw text from the website
url = "https://h1bdata.info/index.php?em=&job=Data+Scientist&city=&year=All+Years"
page = requests.get(url)
htmltext = page.text.strip()

# Declare the soup object
soup = BeautifulSoup(htmltext, 'lxml')

# Get the table
table = soup.find('table',{'class':'tablesorter tablesorter-blue hasStickyHeaders'})
# Get the dataframe, tr is the table row, which consists all elements
rows = list(table.find_all('tr'))

# Take all row elements and make it as 2-d array
df = []
for row in rows:
	temp =[]
	elems = row.children
	for elem in elems:
		temp.append(elem.get_text())
	df.append(temp)

# Convert the 2-d array become pandas dataframe
raw_data = pd.DataFrame(df[1:], columns=df[0])
# Only using data that is certified, drop withdraw or denied
data = raw_data.loc[raw_data['CASE STATUS']=='CERTIFIED']
# Replace comma so that Python able to convert to number
data['BASE SALARY'] = data['BASE SALARY'].apply(lambda x: float(x.replace(',','')))
# Aggregate for mean
data = data.groupby('LOCATION')['BASE SALARY'].mean()

# Obtain the lon and lat for major cities
url = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=1000-largest-us-cities-by-population-with-geographic-coordinates&rows=1000&sort=-rank&facet=city&facet=state"
coord_json = simplejson.load(urllib.request.urlopen(url))

# Obtain the data from json files downloaded
rows = coord_json['records']
coord_raw = []
for row in rows:
	content = row['fields']
	coord_raw.append([content['city'],content['state'],
		             content['coordinates'][0],content['coordinates'][1]])

# Convert data back to DataFrame and location was converted to index
data = pd.DataFrame(data)
data['LOCATION'] = data.index

# Convert coord to dataframe
coord = pd.DataFrame(coord_raw, columns=['city','state','latitude','longitude'])
# Split city and state from location
data['CITY'], data['STATE'] = data.LOCATION.str.split(', ', 1).str
# Match capitalize between dataframe
data['CITY'] = data['CITY'].str.lower()
data['CITY'] = data['CITY'].str.capitalize()
# Convert the State Abb to State name in full spelling
# The file is obtained from USPS
state = pd.read_csv('state.csv').values
state_dict = dict()
for i in state:
	state_dict[i[1]] =i[0]
data['STATE'] = data['STATE'].replace(state_dict)
# Inner join two dataframe, just lazy to deal with null values
data = data.merge(coord, how='inner', left_on=['CITY','STATE'],
                  right_on=['city','state'])
# Make a column for text display
data['text'] = 'Average H1B Salary in ' + data['CITY']+', ' +\
                data['STATE'] + ':$ ' +\
                round(data['BASE SALARY'],2).astype(str)
# Assign colours
scl = [ [0,'rgb(255, 0, 0)'], [0.2,'rgb(255, 51 ,0)'], [0.4,'rgb(255, 102, 0)'] ,\
        [0.6,'rgb(255, 153, 0)'],[0.8,'rgb(255, 204, 0)'], [1,'rgb(255, 255, 0)'] ]
# Plotly data
data_plot = [ go.Scattergeo(locationmode='USA-states',
	                        lon=data['longitude'],
	                        lat=data['latitude'],
	                        text=data['text'],
	                        mode='markers',
	                        marker = dict( 
				            size = 8, 
				            opacity = 0.8,
				            reversescale = True,
				            autocolorscale = False,
				            symbol = 'square',
				            line = dict(
				                width=1,
				                color='rgba(102, 102, 102)'
				            ),
				            colorscale = scl,
				            cmin = data['BASE SALARY'].min(),
				            color = data['BASE SALARY'],
				            cmax = data['BASE SALARY'].max(),
				            colorbar=dict(
				                title="Average Salary ($)")))]
# Layout
layout = dict(
        title = 'Data Scientist H1B Base Salary<br>(Hover Cities for Detail)', 
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = "rgb(250, 250, 250)",
            subunitcolor = "rgb(217, 217, 217)",
            countrycolor = "rgb(217, 217, 217)",
            countrywidth = 0.5,
            subunitwidth = 0.5        
        ),
    )
# Plot the Graph
fig = go.Figure(data=data_plot, layout=layout )
plotly.offline.plot(fig, filename='DS_salary.html')
