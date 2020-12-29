import http.client
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as pltDates
import os.path
import json
import math
import datetime
from matplotlib.ticker import NullFormatter, FixedLocator

def getMonthData(year, month):
  URL = "www.top500.org"

  connection = http.client.HTTPSConnection(URL)
  connection.request("GET", "/lists/top500/{}/{}/".format(year, month))
  response = connection.getresponse()

  content = response.read()
  connection.close()

  return content

def getMonthDataFromRawString(rawString):
  soup = BeautifulSoup(rawString, features="html.parser")
  
  tableRows = soup.find('table').find_all('tr')
  criteria = tableRows[0].find_all('th')[3].text
  top3Values = list(map(lambda r: float(r.find_all('td')[3].text.replace(',','')), tableRows[1:4]))

  average = sum(top3Values) / 3

  if "GFlop" in criteria:
    average /= 10 ** 3

  return float(f'{average:.4f}')

def computeAverageYear(dictContent):
  prev = None
  progress = 0

  for yearData in dictContent.values():
    av = (yearData['june'] + yearData['november']) / 2

    if prev == None:
      prev = av
      continue
    
    progress += (av / prev)
    prev = av
  
  return progress / (len(dictContent.keys()) - 1)


DATA_FILE_NAME = './data.json'
OUTPUT_PROGRESS = './output/progres-anual.txt'
OUTPUT_PROGRESS_DIR_NAME = 'output'

if not os.path.exists(DATA_FILE_NAME):
  open(DATA_FILE_NAME, 'w').close()

f = open(DATA_FILE_NAME, 'r+')

dataContent = f.read()
dataContentDict = {} if dataContent == '' else json.loads(dataContent)

startYear = 1993
endYear = 1995

minPerf, maxPerf = math.inf, -math.inf

for year in range(startYear, endYear + 1):
  juneData, novData = None, None
  
  if str(year) in dataContentDict:
    juneData = dataContentDict[str(year)]['june']
    novData = dataContentDict[str(year)]['november']
  else:
    june = '06'
    nov = '11'

    juneData = getMonthDataFromRawString(getMonthData(year, june))
    novData = getMonthDataFromRawString(getMonthData(year, nov))
  

  maxPerf = juneData if juneData > maxPerf else maxPerf
  maxPerf = novData if novData > maxPerf else maxPerf
  minPerf = juneData if juneData < minPerf else minPerf
  minPerf = novData if novData < minPerf else minPerf

  dataContentDict[str(year)] = {
    'june': juneData,
    'november': novData
  }


f.seek(0)
f.truncate()
json.dump(dataContentDict, f)

if not os.path.exists(OUTPUT_PROGRESS_DIR_NAME):
  os.makedirs(OUTPUT_PROGRESS_DIR_NAME)

with open(OUTPUT_PROGRESS, 'w') as file:
  file.write('Progresul mediu anual este {}.'.format(computeAverageYear(dataContentDict)))

yearAxis = []
for year in range(startYear, endYear + 1):
  yearAxis += [datetime.datetime(year, 6, 1), datetime.datetime(year, 11, 1)]

perfAxis = []
for yearPairDict in dataContentDict.values():
  perfAxis += yearPairDict.values()

plt.figure(figsize=(15, 10))

yearAxis = pltDates.date2num(yearAxis)
plt.plot_date(yearAxis, perfAxis, 'o-', linewidth=1, markersize=3)

years = pltDates.YearLocator()   # every year
months = pltDates.MonthLocator()  # every month
years_fmt = pltDates.DateFormatter('%Y')

plt.gca().xaxis.set_major_locator(years)
plt.gca().xaxis.set_major_formatter(years_fmt)
plt.gca().xaxis.set_minor_locator(months)

plt.gca().set_xlim([datetime.date(startYear, 1, 1), datetime.date(endYear, 12, 31)])

plt.ylabel('Perfomanta maxima (TFlop/s)')
plt.xlabel('Anul')
plt.gca().set_title("Evolutia performantei vs. timp")

plt.gca().format_ydata = lambda x: x + 1

plt.yticks(np.arange(0, maxPerf, (maxPerf - minPerf) / 8))

# plt.savefig(
#   './output/graf.png',
#   format='png',
# )