from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import json
import requests

from gradescope_utils.auth import *
from gradescope_utils.config import TIMEOUT
from gradescope_utils.utils import *




def modal_api_request(driver, course: int, id_number: int, name: str):
    assignments = []
    api_url = f"https://www.gradescope.com/courses/{course}/gradebook.json?user_id={id_number}"
    print(f"Making API request: {api_url}")
    
    # Get cookies from the current browser session
    cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    
    response = requests.get(api_url, cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        for item in data:
            assignment = item.get('assignment', {})
            submission = assignment.get('submission', {})
            
            assignment_name = assignment.get('title', 'Unknown Assignment')
            total_points = assignment.get('total_points', 'Unknown')
            score = submission.get('score', 'No submission')
            
            assignments.append({
                "Name": name,
                "Assignment Name": assignment_name,
                "Score": score,
                "Total Points": total_points,
                "Assignment ID": assignment.get('id'),
                "Submission URL": submission.get('url')
            })
    else:
        print(f"API request failed with status {response.status_code}")
        print(f"Response text: {response.text[:200]}...")
        assignments.append({
            "Name": name,
            "Assignment Name": None,
            "Score": None,
            "Total Points": None,
            "Assignment ID": None,
            "Submission URL": None
        })

    return assignments




def pull_roster(driver, course_number: int, timeout=TIMEOUT):
    roster_df = pd.DataFrame(columns=["Name", "Email", "Role", "Sections", "GS_id"])
    
    manual_user_login(driver)
    
    driver.get(f"https://www.gradescope.com/courses/{course_number}/memberships")
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rosterRow"))
        )
        print("Login Success.")
    except:
        raise TimeoutError("Login not completed in time.")
    
    name_buttons = driver.find_elements(By.CSS_SELECTOR, "button.js-rosterName")
    edit_buttons = driver.find_elements(By.CSS_SELECTOR, "button.rosterCell--editIcon")
        
    roster_data = []
    assingments_data = []
    for i in range(len(name_buttons)):
        name = name_buttons[i].text if i < len(name_buttons) else None
        email = None
        role = None
        if i < len(edit_buttons):
            try:
                email = edit_buttons[i].get_attribute("data-email")
                role_num = edit_buttons[i].get_attribute("data-role")
                # Convert role number to text (0=Student, 1=TA, 2=Instructor, etc.)
                role_map = {"0": "Student", "2": "TA", "1": "Instructor"}
                role = role_map.get(role_num, f"Role {role_num}")
            except:
                pass
        
        print(f"Row {i}: Name='{name}', Email='{email}', Role='{role}'")


        button = driver.find_element(By.XPATH, f"//button[@class='js-rosterName' and @data-name='{name}']")
        
        data_url = button.get_attribute('data-url')
        if data_url and 'user_id=' in data_url:
            user_id = data_url.split('user_id=')[1].split('&')[0]
        else:
            print(f"No user_id found in data-url for {name}")
            continue 
        
        assingments = modal_api_request(driver, course_number, user_id, name)

        
        roster_data.append({
            "Name": name,
            "Email": email,
            "Role": role,
            #  TODO fix to work with sections
            "Sections": None
        })

        assingments_data.extend(assingments)
    
    roster_df = pd.DataFrame(roster_data)
    assingments_df = pd.DataFrame(assingments_data)

    
    
    return roster_df, assingments_df

