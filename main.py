import os

from selenium import webdriver
import time, json, requests

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def scrapePage():
    driver = webdriver.Remote("http://selenium:4444/wd/hub", DesiredCapabilities.CHROME)
    # driver = webdriver.Chrome("chromedriver.exe")
    driver.get("https://353-iz.impfterminservice.de/impftermine/service?plz=20357")
    time.sleep(1)
    driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    time.sleep(5)
    jsonData = driver.get("https://353-iz.impfterminservice.de/rest/suche/termincheck?plz=20357&leistungsmerkmale=L920,L921,L922,L923")
    jsonData = driver.find_element_by_css_selector("pre")
    jsonData = jsonData.text

    driver.quit()

    if(jsonData == "{}"):
        pushData = {"token": os.environ['token'], "user": os.environ['user'], "title": "Der Bot wurde gesperrt :(", "priority": "2"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)

    data = json.loads(jsonData)

    available = data["termineVorhanden"]
    types = data["vorhandeneLeistungsmerkmale"]

    print(available)

    if(available):
        pushData = {"token":os.environ['token'],"user":os.environ['user'],"title":"Es gibt Impfterminee!!!", "priority":"2"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)


    pushData = {"token":os.environ['token'],"user":os.environ['user'],"title":"Es gibt Impfterminee!!!", "priority":"2"}
    requests.post("https://api.pushover.net/1/messages.json", pushData)

while(True):
    scrapePage()
    time.sleep(300)