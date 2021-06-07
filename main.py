import os, time, json, requests, selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy, ProxyType

# Send Test Message to show that the application is running
pushData = {"token":os.environ['token'],"user":os.environ['user'],"message":"Die APP wurde neu gestartet", "priority":"-2"}
request = requests.post("https://api.pushover.net/1/messages.json", pushData)

# Locations Array is defined in the following structure: Array[Array[Name, Vaccination Center Page, REST Api for appointment check]]
locations = [["Hamburg Messehallen","https://353-iz.impfterminservice.de/impftermine/service?plz=20357", "https://353-iz.impfterminservice.de/rest/suche/termincheck?plz=20357&leistungsmerkmale=L920,L921,L922,L923"],["Tübingen Impfzentrum","https://003-iz.impfterminservice.de/impftermine/service?plz=72072", "https://003-iz.impfterminservice.de/rest/suche/termincheck?plz=72072&leistungsmerkmale=L920,L921,L922,L923"]]
# locations = [["Hamburg Messehallen","https://353-iz.impfterminservice.de/impftermine/service?plz=20357", "https://353-iz.impfterminservice.de/rest/suche/termincheck?plz=20357&leistungsmerkmale=L920,L921,L922,L923"]]
# servers = ["http://selenium:4444/wd/hub","http://10.0.0.3:4444/wd/hub","http://10.0.0.4:4444/wd/hub","http://10.0.0.5:4444/wd/hub","http://10.0.0.2:4444/wd/hub"]
servers = ["http://selenium:4444/wd/hub"]
def scrapePage(locationData, remote):
    # Click through the impftermineservice page to act like a human lol
    PROXY = "http://tor:8118"  # IP:PORT or HOST:PORT
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    driver = webdriver.Remote(remote, DesiredCapabilities.CHROME, None, None, False, None, chrome_options)

    driver.get("http://api.ipify.org/")
    ip = driver.find_element_by_css_selector("pre")
    print("Current IP: "+ip)


    driver.get(locationData[1])
    try:
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    except:
        try:
            while True:
                driver.find_element_by_css_selector("div.clock")
                print("Waiting room...")
                time.sleep(2)
        except:
            print("We are through")
            time.sleep(2)
            driver.find_element_by_css_selector(
                "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    time.sleep(5)
    driver.get(locationData[2])
    # Get Json Data which shows available appointments
    jsonData = driver.find_element_by_css_selector("pre")
    jsonData = jsonData.text

    # If the response is {} we probably got detected and our IP is blocked. Therefore we wait 10 minutes until we continue
    if(jsonData == "{}"):
        driver.quit()
        pushData = {"token": os.environ['token'], "user": os.environ['user'], "message": "Der Bot "+remote+" wurde in "+locationData[0]+" gesperrt :(", "priority": "1"}
        requests.post("https://api.pushover.net/1/messages.json", pushData)
        time.sleep(30)
    else:
        # Decode json data
        data = json.loads(jsonData)

        # Map json data to variables
        available = data["termineVorhanden"]
        types = data["vorhandeneLeistungsmerkmale"]

        # If an appointment is available send an notification to your device, if not send a message without notification which is shown in the Pushover App
        if(available):
            try:
                pushData = {"token":os.environ['token'],"user":os.environ['user'],"title":"Es gibt Impftermine in "+locationData[0]+" !!!", "message": json.dumps(types), "priority":"1"}
                requests.post("https://api.pushover.net/1/messages.json", pushData)
                driver.get(locationData[1])
                time.sleep(1)
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(1) > span").click()
                time.sleep(1)
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(1) > label > input").send_keys(os.environ['code1'])
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(3) > label > input").send_keys(os.environ['code2'])
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(5) > label > input").send_keys(os.environ['code3'])
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(2) > button").click()
                time.sleep(5)
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-search > div > div > div:nth-child(2) > div > div > div:nth-child(5) > div > div:nth-child(1) > div.its-search-step-body > div.its-search-step-content > button").click()
                time.sleep(2)
                availableSlots = driver.find_element_by_css_selector("#itsSearchAppointmentsModal > div > div > div.modal-body > div > div > form > div.d-flex.flex-column.its-slot-pair-search-info > span").text
                pushData = {"token": os.environ['token'], "user": os.environ['user'], "title": "Es gibt Impftermine in " + locationData[0] + " !!!", "message": availableSlots, "priority": "1"}
                requests.post("https://api.pushover.net/1/messages.json", pushData)
                driver.quit()
                # Wait to not enter same code more than one time per 10 minutes
                time.sleep(600)
            except selenium.common.exceptions.NoSuchElementException:
                driver.quit()
                print("Request was buggy")

        else:
            print("Impftermine in " + locationData[0] + " mit Server "+remote+" geprüft, gibt aber keine :( " + time.strftime("%H:%M:%S"))
            driver.quit()

while(True):
    # Wait until the selenium container initialized
    time.sleep(25)
    if(int(time.strftime("%H")) > 19):
        pushData = {"token": os.environ['token'], "user": os.environ['user'], "message": "Die APP geht schlafen", "priority": "-2"}
        request = requests.post("https://api.pushover.net/1/messages.json", pushData)
        time.sleep(25200)
    for server in servers:
        for location in locations:
            scrapePage(location, server)
            time.sleep(10)
        time.sleep(60)