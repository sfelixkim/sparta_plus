from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
import requests


client = MongoClient('localhost', 27017)
db = client.dbsparta_plus_week3

driver = webdriver.Chrome('chromedriver')

url = "http://matstar.sbs.co.kr/location.html"

driver.get(url)
time.sleep(5)
count = 0
while True:
    try:
        btn_more = driver.find_element_by_css_selector("#foodstar-front-location-curation-more-self > div > button")
        btn_more.click()
        count+=1
        print(count)
        if count>100: break
        time.sleep(5)
    except (NoSuchElementException, AttributeError, KeyboardInterrupt):
        break

print(count)
req = driver.page_source
driver.quit()

soup = BeautifulSoup(req, 'html.parser')

places = soup.select("ul.restaurant_list > div > div > li > div > a")

print(len(places))
for place in places:
    title = place.select_one("strong.box_module_title").text
    address = place.select_one("div.box_module_cont > div > div > div.mil_inner_spot > span.il_text").text
    category = place.select_one("div.box_module_cont > div > div > div.mil_inner_kind > span.il_text").text
    show, episode = place.select_one("div.box_module_cont > div > div > div.mil_inner_tv > span.il_text").text.rsplit(" ", 1)

    headers = {
        "X-NCP-APIGW-API-KEY-ID": "1jejchnryy",
        "X-NCP-APIGW-API-KEY": "9R5YWwWHxJZkl2OTLJ4dV4j4SXl8DetSaBBVYCtM"
    }
    r = requests.get(f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}", headers=headers)
    response = r.json()
    if response["status"] == "OK":
        if len(response["addresses"]) > 0:
            x = float(response["addresses"][0]["x"])
            y = float(response["addresses"][0]["y"])
            print(title, address, category, show, episode, x, y)
            doc = {
                "title": title,
                "address": address,
                "category": category,
                "show": show,
                "episode": episode,
                "mapx": x,
                "mapy": y}
            db.matjips.insert_one(doc)
        else:
            print(title, "좌표를 찾지 못했습니다")
    else:
        print(response["status"])
