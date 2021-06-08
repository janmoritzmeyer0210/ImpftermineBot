import os, time, json, requests, selenium

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException


# Send Test Message to show that the application is running
pushData = {"chat_id":"-1001499214177","text":"Die APP wurde neu gestartet"}
request = requests.post("https://api.telegram.org/bot"+os.environ['telegram']+"/sendMessage", pushData)

# Locations Array is defined in the following structure: Array[Array[Name, Vaccination Center Page, REST Api for appointment check]]
locations = json.loads(os.environ['locations'])

def check_exists_by_css_selector(selector, webdriver):
    try:
        webdriver.find_element_by_xpath(selector)
    except NoSuchElementException:
        return False
    return True


def scrapePage(locationData, remote):
    # Click through the impftermineservice page to act like a human lol
    PROXY = os.environ['proxy']
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    driver = webdriver.Remote(remote, DesiredCapabilities.CHROME, None, None, False, None, chrome_options)

    driver.get("http://api.ipify.org/")
    ip = driver.find_element_by_css_selector("pre")
    ip = ip.text


    driver.get(locationData[1])
    for x in range(50):
        print(x)
        if check_exists_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small" ,driver):
            print("Side loading took "+x/2+" seconds")
            break;
        if check_exists_by_css_selector("div.clock" ,driver):
            print("Side loading took " + x / 2 + " seconds")
            break;
        time.sleep(0.5)
    try:
        driver.find_element_by_css_selector(
            "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    except Exception as e:
        print('Failed clicking button: '+str(e))
        try:
            for x in range(locationData[4]):
                driver.find_element_by_css_selector("div.clock")
                pushData = {"chat_id": "-1001499214177", "text": "Waiting room in "+locationData[0]+"..."}
                requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
                time.sleep(10)
        except:
            print("We are through")
            time.sleep(2)
            driver.find_element_by_css_selector(
                "body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(2) > span > small").click()
    time.sleep(5)
    driver.get(locationData[2])
    # Get Json Data which shows available appointments
    try:
        jsonData = driver.find_element_by_css_selector("pre")
        jsonData = jsonData.text
    except:
        pushData = {"chat_id": "-1001499214177", "text": "Es gab einen Bug, Webdata: " + driver.page_source}
        requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
        jsonData = "{}"

    # If the response is {} we probably got detected and our IP is blocked. Therefore we wait 10 minutes until we continue
    if(jsonData == "{}"):
        driver.quit()
        pushData = {"chat_id": "-1001499214177", "text": "Der Bot wurde in "+locationData[0]+" mit der IP "+ip+" gesperrt oder der Warteraum wurde abgebrochen :("}
        requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
        time.sleep(5)
    else:
        # Decode json data
        data = json.loads(jsonData)

        # Map json data to variables
        available = data["termineVorhanden"]
        types = data["vorhandeneLeistungsmerkmale"]

        # If an appointment is available send an notification to your device, if not send a message without notification which is shown in the Pushover App
        if(available):
            try:
                silent = False
                types_str = ""
                for type in types:
                    if type == "L920":
                        types_str = types_str + "BioNTech"
                    elif type == "L921":
                        types_str = types_str + "Moderna"
                    elif type == "L922":
                        types_str = types_str + "AstraZeneca"
                        silent = True
                    elif type == "L923":
                        types_str = types_str + "Johnson & Johnson"
                        silent = True

                pushData = {"chat_id": locationData[3], "text": "Es gibt Impftermine in "+locationData[0]+" für folgende Stoffe: " + types_str+". Buchbar unter folgendem Link: "+locationData[1], "disable_notification":silent}
                requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
                driver.get(locationData[1])
                time.sleep(1)
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(2) > div > div > label:nth-child(1) > span").click()
                time.sleep(1)
                code = locations[5]
                code = code.split("-")
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(1) > label > input").send_keys(code[0])
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(3) > label > input").send_keys(code[1])
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(1) > label > app-ets-input-code > div > div:nth-child(5) > label > input").send_keys(code[2])
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-login > div > div > div:nth-child(2) > app-its-login-user > div > div > app-corona-vaccination > div:nth-child(3) > div > div > div > div.ets-login-form-section.in > app-corona-vaccination-yes > form > div:nth-child(2) > button").click()
                time.sleep(5)
                driver.find_element_by_css_selector("body > app-root > div > app-page-its-search > div > div > div:nth-child(2) > div > div > div:nth-child(5) > div > div:nth-child(1) > div.its-search-step-body > div.its-search-step-content > button").click()
                time.sleep(2)
                availableSlots = driver.find_element_by_css_selector("#itsSearchAppointmentsModal > div > div > div.modal-body > div > div > form > div.d-flex.flex-column.its-slot-pair-search-info > span").text
                pushData = {"chat_id": locationData[3], "text": "Es gibt Impftermine in " + locationData[0] + " !!! "+locationData[1]+ " "+availableSlots}
                requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
                driver.quit()
                # Wait to not enter same code more than one time per 10 minutes
                time.sleep(600)
            except selenium.common.exceptions.NoSuchElementException:
                driver.quit()
                pushData = {"chat_id": "-1001499214177", "text": "Request was buggy "+driver.page_source}
                requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)

        else:
            print("Impftermine in " + locationData[0] + " mit IP "+ip+" geprüft, gibt aber keine :( " + time.strftime("%H:%M:%S"))
            pushData = {"chat_id": "-1001499214177", "text": "Impftermine in " + locationData[0] + " mit IP "+ip+" geprüft, gibt aber keine :( " + time.strftime("%H:%M:%S")}
            requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
            driver.quit()

# Wait until the selenium container initialized
time.sleep(25)
while(True):
    # if(int(time.strftime("%H")) > 22):
    #     pushData = {"token": os.environ['token'], "user": os.environ['user'], "message": "Die APP geht schlafen", "priority": "-2"}
    #     request = requests.post("https://api.pushover.net/1/messages.json", pushData)
    #     pushData = {"chat_id": "-1001499214177", "text": "Die APP geht schlafen"}
    #     requests.post("https://api.telegram.org/bot" + os.environ['telegram'] + "/sendMessage", pushData)
    #     time.sleep(25200)
    for location in locations:
        scrapePage(location, os.environ['selenium'])
        time.sleep(10)