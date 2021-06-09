import os, time, json, requests, selenium, threading, cloudscraper

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException


# Send Test Message to show that the application is running
pushData = {"chat_id":"-1001499214177","text":"Die APP wurde neu gestartet"}
requests.post("https://api.telegram.org/bot"+os.environ['telegram']+"/sendMessage", pushData)

# Locations Array is defined in the following structure: Array[Array[Name, Vaccination Center Page, REST Api for appointment check]]
locations = json.loads(os.environ['locations'])

driver = None
ip = None
types = None
cookies = None
proxies = {"http": os.environ['proxy']}

scraper = cloudscraper.create_scraper()


def check_exists_by_css_selector(selector, webdriver):
    try:
        webdriver.find_element_by_css_selector(selector)
    except NoSuchElementException:
        return False
    return True

def initDriver():
    global driver, ip
    PROXY = os.environ['proxy']
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    driver = webdriver.Remote(os.environ['selenium'], DesiredCapabilities.CHROME, None, None, False, None, chrome_options)

    ipres = scraper.get("http://api.ipify.org/", proxies=proxies)
    ip = ipres.text
    print(ip)

def checkForAppointments(locationData):
    global types, driver, scraper, ip
    res = scraper.get(locationData[2], proxies=proxies)
    jsonData = res.text

    # If the response is {} we probably got detected and our IP is blocked. Therefore we wait 10 minutes until we continue
    if (jsonData == "{}"):
        pushData = {"chat_id": "-1001499214177", "text": "Der Bot wurde in " + locationData[0] + " mit der IP " + ip + " gesperrt oder der Warteraum wurde abgebrochen :("}
        requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
        time.sleep(5)
        cookies = generateCookie(locationData)
        return False
    else:
        # Decode json data
        data = json.loads(jsonData)

        # Map json data to variables
        available = data["termineVorhanden"]
        types = data["vorhandeneLeistungsmerkmale"]
        pushData = {"chat_id": "-1001499214177", "text": "Impftermine in " + locationData[
            0] + " mit IP " + ip + " geprüft, gibt aber keine :( " + time.strftime("%H:%M:%S")}
        requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
        return available

def sendMessage(locationData):
    global driver
    try:
        silent = False
        types_str = ""
        chat_id = "-1001499214177"
        for type in types:
            if type == "L920":
                types_str = types_str + "BioNTech"
                chat_id = locationData[3]
            elif type == "L921":
                types_str = types_str + "Moderna"
                chat_id = locationData[3]
            elif type == "L922":
                types_str = types_str + "AstraZeneca (nur für 60+ buchbar)"
                silent = True
                chat_id = locationData[4]
            elif type == "L923":
                types_str = types_str + "Johnson & Johnson (nur für 60+ buchbar)"
                silent = True
                chat_id = locationData[4]


        initDriver()
        pushData = {"chat_id": chat_id, "text": "Es gibt Impftermine in " + locationData[
            0] + " für folgende Stoffe: " + types_str + ". Buchbar unter folgendem Link: " + locationData[1],
                    "disable_notification": silent}
        requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
        driver.get(locationData[1])
        time.sleep(1)
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(1) > span").click()
        time.sleep(1)
        code = locationData[6]
        code = code.split("-")
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(1) > label > input").send_keys(
            code[0])
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(3) > label > input").send_keys(
            code[1])
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(5) > label > input").send_keys(
            code[2])
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(2) > button").click()
        time.sleep(5)
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-search > div > div > div:nth-child(2) > div > div > div:nth-child(5) > div > div:nth-child(1) > div.its-search-step-body > div.its-search-step-content > button").click()
        time.sleep(2)
        availableSlots = driver.find_element_by_css_selector(
            "#itsSearchAppointmentsModal > div > div > div.modal-body > div > div > form > div.d-flex.flex-column.its-slot-pair-search-info > span").text
        pushData = {"chat_id": "-1001499214177",
                    "text": "Bei der Test-Buchung gab es folgende Nachricht: " + availableSlots + locationData[0] + types_str}
        requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
        driver.quit()
        # Wait to not enter same code more than one time per 10 minutes
        time.sleep(600)
    except selenium.common.exceptions.NoSuchElementException as e:
        print('Failed clicking button: ' + str(e))
        pushData = {"chat_id": "-1001499214177", "text": "Request was buggy " + driver.page_source}
        requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
        driver.quit()

def closeDriver(locationData):
    global driver
    pushData = {"chat_id": "-1001499214177", "text": "Impftermine in " + locationData[
        0] + " mit IP " + ip + " geprüft, gibt aber keine :( " + time.strftime("%H:%M:%S")}
    requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
    driver.quit()


def generateCookie(locationData):
    global driver
    initDriver()
    driver.get(locationData[1])
    for x in range(50):
        if check_exists_by_css_selector(
                "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small",
                driver):
            break;
        if check_exists_by_css_selector("div.clock", driver):
            break;
        time.sleep(0.5)
    try:
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    except Exception as e:
        print('Failed clicking button: ' + str(e))
        try:
            for x in range(locationData[5]):
                driver.find_element_by_css_selector("div.clock")
                pushData = {"chat_id": "-1001499214177", "text": "Waiting room in " + locationData[0] + "..."}
                requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
                time.sleep(10)
        except:
            print("We are through")
            time.sleep(2)
            driver.find_element_by_css_selector(
                "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    time.sleep(5)
    cookie = driver.get_cookie("bm_sz").get("value")
    scraper.cookies.update({"bm_sz": cookie})
    pushData = {"chat_id": "-1001499214177", "text": "Es wurden Cookies für " + locationData[0] + " generiert:" + cookie}
    requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
    driver.quit()


def threadForLocation(locationData):
    pushData = {"chat_id": "-1001499214177", "text": "Ein Thread für "+locationData[0]+" wurde gestartet"}
    requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
    while (True):
        if checkForAppointments(locationData):
            consistent = True
            for x in range(location[7]):
                time.sleep(10)
                if not checkForAppointments(location):
                    consistent = False
            if consistent:
                sendMessage(location)
        time.sleep(30)

# Wait until the selenium and tor containers are initialized
time.sleep(25)
for location in locations:
    x = threading.Thread(target=threadForLocation, args=(location,))
    x.start()
    time.sleep(60)

while True:
    time.sleep(100)
