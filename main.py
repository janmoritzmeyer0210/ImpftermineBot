import os, time, json, requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Send Test Message to show that the application is running
pushData = {"token":os.environ['token'],"user":os.environ['user'],"message":"Die APP wurde neu gestartet", "priority":"-2"}
request = requests.post("https://api.pushover.net/1/messages.json", pushData)

# Locations Array is defined in the following structure: Array[Array[Name, Vaccination Center Page, REST Api for appointment check]]
locations = [["Hamburg Messehallen","https://353-iz.impfterminservice.de/impftermine/service?plz=20357", "https://353-iz.impfterminservice.de/rest/suche/termincheck?plz=20357&leistungsmerkmale=L920,L921,L922,L923"],["Tübingen Impfzentrum","https://003-iz.impfterminservice.de/impftermine/service?plz=72072", "https://003-iz.impfterminservice.de/rest/suche/termincheck?plz=72072&leistungsmerkmale=L920,L921,L922,L923"]]

def scrapePage(locationData):
    # Click through the impftermineservice page to act like a human lol
    driver = webdriver.Remote("http://selenium:4444/wd/hub", DesiredCapabilities.CHROME)
    driver.get(locationData[1])
    time.sleep(1)
    driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    time.sleep(5)
    driver.get(locationData[2])
    # Get Json Data which shows available appointments
    jsonData = driver.find_element_by_css_selector("pre")
    jsonData = jsonData.text

    driver.quit()

    # If the response is {} we probably got detected and our IP is blocked. Therefore we wait 10 minutes until we continue
    if(jsonData == "{}"):
        pushData = {"token": os.environ['token'], "user": os.environ['user'], "message": "Der Bot wurde gesperrt :(", "priority": "1"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)
        time.sleep(600)

    # Decode json data
    data = json.loads(jsonData)

    # Map json data to variables
    available = data["termineVorhanden"]
    types = data["vorhandeneLeistungsmerkmale"]

    # If an appointment is available send an notification to your device, if not send a message without notification which is shown in the Pushover App
    if(available):
        pushData = {"token":os.environ['token'],"user":os.environ['user'],"title":"Es gibt Impftermine in "+locationData[0]+" !!!", "message": json.dumps(types), "priority":"1"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)
    else:
        pushData = {"token": os.environ['token'], "user": os.environ['user'], "message": "Impftermine in " + locationData[0] + " geprüft, gibt aber keine :(", "priority": "-2"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)

while(True):
    # Wait until the selenium container initialized
    time.sleep(10)
    for location in locations:
        scrapePage(location)
    time.sleep(150)