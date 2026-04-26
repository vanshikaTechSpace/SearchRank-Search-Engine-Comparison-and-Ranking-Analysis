from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup_driver(headless_mode: bool, user_agent: str):
    """
    Sets up the Chrome WebDriver with the specified options.
    """
    options = Options()

    if headless_mode:
        options.add_argument("--headless=new")

    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--window-size=1920,1080")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver
