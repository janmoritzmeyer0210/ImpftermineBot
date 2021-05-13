import os, time, json, requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

pushData = {"token":os.environ['token'],"user":os.environ['user'],"title":"Die APP wurde neu gestartet","message":"Lol", "priority":"1"}
request = requests.post("https://api.pushover.net/1/messages.json", pushData)

locations = [["Hamburg Messehallen","https://353-iz.impfterminservice.de/impftermine/service?plz=20357", "https://353-iz.impfterminservice.de/rest/suche/termincheck?plz=20357&leistungsmerkmale=L920,L921,L922,L923"],["Tübingen Impfzentrum","https://003-iz.impfterminservice.de/impftermine/service?plz=72072", "https://003-iz.impfterminservice.de/rest/suche/termincheck?plz=72072&leistungsmerkmale=L920,L921,L922,L923"]]

def scrapePage(data):
    driver = webdriver.Remote("http://selenium:4444/wd/hub", DesiredCapabilities.CHROME)
    driver.get(data[1])
    time.sleep(1)
    driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    time.sleep(5)
    driver.get(data[2])
    jsonData = driver.find_element_by_css_selector("pre")
    jsonData = jsonData.text

    driver.quit()

    if(jsonData == "{}"):
        pushData = {"token": os.environ['token'], "user": os.environ['user'], "message": "Der Bot wurde gesperrt :(", "priority": "1"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)
        time.sleep(600)

    data = json.loads(jsonData)

    available = data["termineVorhanden"]
    types = data["vorhandeneLeistungsmerkmale"]

    print(available)

    if(available):
        pushData = {"token":os.environ['token'],"user":os.environ['user'],"title":"Es gibt Impftermine in "+data[0]+" !!!", "message": json.dumps(types), "priority":"1"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)

while(True):
    time.sleep(10)
    for location in locations:
        scrapePage(location)
    time.sleep(150)