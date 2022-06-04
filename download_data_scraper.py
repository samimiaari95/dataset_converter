from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By



# Open chrome
driver = webdriver.Chrome('./chromedriver')

#driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#time.sleep(1)
#driver.execute_script("window.scrollTo(0, 0);")
#height = driver.execute_script("return document.body.scrollHeight")
#for x in range(height):
#    driver.execute_script("window.scrollBy(0, 1);")
for year in range(1980, 2022):
    for month in range(5,13):
        month = str(month).zfill(2)
        url = f"https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2T1NXLND.5.12.4/{year}/{month}/"
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source)

        all_data = driver.find_elements_by_xpath("//a[contains(@href, '.nc4')]")
        for element in all_data:
            if not element.text:
                all_data.remove(element)
        for element in all_data:
            if "xml" in element.text:
                all_data.remove(element)
        print(f'length of {month} in year {year}: {len(all_data)}')

        for i in range(len(all_data)):
            url = f"https://goldsmr4.gesdisc.eosdis.nasa.gov/data/MERRA2/M2T1NXLND.5.12.4/{year}/{month}/"
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source)
            all_data = driver.find_elements_by_xpath("//a[contains(@href, '.nc4')]")
            for element in all_data:
                if not element.text:
                    all_data.remove(element)
            for element in all_data:
                if "xml" in element.text:
                    all_data.remove(element)
            oneday = all_data[i].click()
            print(f'Downloading day {i+1}')
            time.sleep(60)
        #driver.close()
print("finally finished")


