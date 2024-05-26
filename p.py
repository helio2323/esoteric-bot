from selenium import webdriver
from selenium.webdriver.chrome.options import Options



options = Options()
options.add_argument("--enable-automation")
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--kiosk-printing")

driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub", options=options)

driver.get("https://www.google.com")    