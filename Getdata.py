import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup

url = "https://h1bdata.info/index.php?em=&job=Data+Scientist&city=&year=All+Years"
page = requests.get(url)
htmltext = page.text.strip()

soup = BeautifulSoup(htmltext, 'lxml')

#table = soup.find_all('table',{'class':'tablesorter tablesorter-blue hasStickyHeaders'})
table = soup.find('table',{'class':'tablesorter tablesorter-blue hasStickyHeaders'})
headers = table.find_all('th')
rows = list(table.find_all('tr'))


df_header = []
for elem in headers:
	df_header.append(elem.get_text())

df = []
for row in rows:
	temp =[]
	elems = row.children
	for elem in elems:
		temp.append(elem.get_text())
	df.append(temp)

df = pd.DataFrame(df, columns=df_header)
print(df)