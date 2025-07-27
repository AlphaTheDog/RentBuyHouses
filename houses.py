from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import re
import time
import pandas as pd
import numpy as np
from urllib.parse import urljoin
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

options=Options()
options.add_argument("--load-extension=/home/marikothee/Desktop/Source/webScraping")
options.add_argument("--start-maximized")
url="https://www.buyrentkenya.com/houses-for-rent"
driver=webdriver.Chrome(options=options)
driver.get(url)

cookies=WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.ID,"onetrust-accept-btn-handler")))
driver.execute_script("arguments[0].scrollIntoView()",cookies)
driver.execute_script("arguments[0].click()",cookies)
#time.sleep(5)
data=list()

def get_data(driver):
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    #time.sleep(5)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "listing-card")))
    soup=BeautifulSoup(driver.page_source)
    items=soup.find_all('div','listing-card')
    for  item in items:
        details=item.find('div','flex flex-row').find(
        {
            'div':['flex flex-col gap-y-3 w-full md:w-4/5','flex flex-col gap-y-3 w-full']
        })
        links=item.find('div','md:w-3/5 relative flex flex-col justify-between px-3 py-4 md:px-5').find('a','absolute left-0 top-0 z-10 h-full w-full')
        link=links.get_attribute_list('href')
        link=''.join(link)
        house_url=urljoin(url,link)
        title=details.find('h2','font-semibold md:hidden').get_text(strip=True)
        desc=details.find('h3','capitalize flex').find('span','relative top-[2px] hidden text-lg font-semibold leading-6 text-black md:inline').get_text(strip=True)
        location=details.find('div','flex flex-wrap gap-x-2 gap-y-1').div.p.get_text(strip=True)
        price=details.find(
           {'div':['flex items-center justify-center text-xl font-bold leading-7 text-grey-900',
                   'inline-flex justify-between text-xl font-bold leading-7 text-grey-850 md:hidden']
            }).get_text(strip=True)
        try:
            pattern=r"\d+,\d+"
            match=re.search(pattern,price)
            price=match.group()
        except:
            price=np.nan
        try:
            link_agency=item.find('div','flex items-center justify-between space-x-1 pt-2 md:h-[48px] md:space-x-0').find('div','block md:hidden').a
            agency=link_agency.get_attribute_list('agency-slug')
            agency=''.join(agency)
        except:
            agency=np.nan
    
        wrapper=item.find('div','flex w-full flex-col gap-y-3').find('div','swiper-wrapper space-x-2')
        try:
            bedrooms=wrapper.find('div','swiper-slide flex h-6 !w-auto items-center rounded-full bg-highlight px-2 py-1 text-sm font-normal leading-4 text-grey-550 swiper-slide-active')
            #label=bedrooms.get_attribute_list('data-cy')
            beds=bedrooms.span.get_text(strip=True)
            pattern=r"\d+"
            match=re.search(pattern,beds)
            beds=match.group()
        except:
            bed=np.nan
        try:
            bathrooms=wrapper.find('div','swiper-slide flex h-6 !w-auto items-center rounded-full bg-highlight px-2 py-1 text-sm font-normal leading-4 text-grey-550 swiper-slide-next')
            baths=bathrooms.span.get_text(strip=True)
            pattern=r"\d+"
            match=re.search(pattern,baths)
            baths=match.group()
        except:
            baths=np.nan
        data.append(
        {
            'title':title,
            'location':location,
            'price':price,
            'bedrooms':beds,
            'bathrooms':baths,
            'agency':agency,
            'link':house_url,
            'desc':desc
        } )

pages=driver.find_element(By.CLASS_NAME,"pagination-page-nav").find_elements(By.TAG_NAME,"li")
total=int(pages[-1].find_element(By.TAG_NAME,"a").text)
for page in range(1,total):
    get_data(driver)
    next=driver.find_elements(By.XPATH,"//div[@class='mt-4 flex w-full flex-row items-center justify-center space-x-1 md:space-x-3']/a")
    driver.execute_script("arguments[0].click()",next[-1])
    time.sleep(20)

driver.quit()

fields=['title','location','price','bedrooms','bathrooms','agency','link','desc']
with open('houses_new.csv','w',newline='')as obj:
    writer=csv.DictWriter(obj,fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)