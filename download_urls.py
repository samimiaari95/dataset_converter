
from bs4 import BeautifulSoup
import requests

from bs4 import BeautifulSoup
import requests
import lxml
import cchardet
import lxml
import cchardet
from bs4 import BeautifulSoup
import time


requests_session = requests.Session()
links = []
for year in range(1980, 2022):
    for month in range(1,13):
        month = str(month).zfill(2)
        url = f"https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2T1NXLND.5.12.4/{year}/{month}/"
        rq = requests_session.get(url)
        soup = BeautifulSoup(rq.content, 'lxml')
        containers = soup.findAll('td', attrs={'valign': 'top'})
        for container in containers:
            try:
                a = container.find('a', href=True)
                link = a.get('href')
                if "xml" not in link and "nc4" in link:
                    print(link)
                    link = f"https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2T1NXLND.5.12.4/{year}/{month}/{link}"
                    links.append(link)
            except:
                print("exception")
f=open(r'C:\Users\Sami\Desktop\tesi_desk\datasets\test_hdf_to_tiff\soilmoisture\soilmoisture.txt','w')
for ele in links:
    f.write(ele+'\n')

f.close()
print("finally finished")


