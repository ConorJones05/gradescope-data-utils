from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from gradescope_utils.config import TIMEOUT

def manual_user_login(driver, timeout=TIMEOUT):
    driver.get("https://www.gradescope.com/saml")
    print("=" * 70)
    print("Please login to gradescope")
    print("=" * 70)

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "courseList"))
        )
        print("Login Success.")
    except:
        raise TimeoutError("Login not completed in time.")



