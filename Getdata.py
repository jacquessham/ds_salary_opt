import requests
import pandas as pd
from bs4 import BeautifulSoup


# Request the html file and extract the raw text from the website
url = "https://h1bdata.info/index.php?em=&job=Data+Scientist&city=&year=All+Years"
page = requests.get(url)
htmltext = page.text.strip()

# Declare the soup object
soup = BeautifulSoup(htmltext, 'lxml')

# table = soup.find_all('table',{'class':'tablesorter tablesorter-blue hasStickyHeaders'})

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
df = pd.DataFrame(df[1:], columns=df[0])
df.to_csv('salary.csv',index=False)

#df_case = df['EMPOLYER','CASE STATUS'].groupby(['EMPOLYER','CASE STATUS']).agg('count')
#print(df_case)

