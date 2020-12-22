import http.client

from bs4 import BeautifulSoup


'''
in dubii
  * 1995/noiembrie - 404
  * (1)
  * media pe luna/an - toate luniile sau doar top 3 dintr o luna
  * realizează media pe luna/an - `/` - ???
  * la ce tb sa facem grafic - perf vs timp

plan!

* get content of https://www.top500.org/
* obtinem primele 3 cele mai puternice
  * (1) (? - sortarea) pt fiecare an - luam din ambele luni, le merge-uim si aflam top 3(sort desc dupa RMAX)
* media pe luna/an
  * pt fiecare luna, facem media artimetica(RMAX) pt toate rez
'''

url = "www.top500.org"

connection = http.client.HTTPSConnection(url)
# connection.request("GET", "/lists/top500/")
connection.request("GET", "/lists/top500/2019/11/")
response = connection.getresponse()
print("Status: {} and reason: {}".format(response.status, response.reason))

content = response.read()
connection.close()

soup = BeautifulSoup(content, features="html.parser")

print(soup.find('table').find_all('tr'))