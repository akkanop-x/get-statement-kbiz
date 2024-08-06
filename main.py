from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


service = Service()
driver = webdriver.Chrome(service=service)

driver.get('https://kbiz.kasikornbank.com/authen/login.jsp?lang=th')

elements = driver.find_element(By.NAME, 'userName').send_keys("YOUR_USERNAME")
elements = driver.find_element(By.NAME, 'password').send_keys("YOUR_PASSWORD")
login_button = driver.find_element(By.ID, "loginBtn")
login_button.click()

account_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'a-center pointer') and contains(text(), 'ดูรายละเอียดบัญชีเพิ่มเติม')]"))
)

account_button.click()

date_input_from = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "createDateFrom"))
)
date_input_to = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "createDateTo"))
)

driver.execute_script("arguments[0].removeAttribute('readonly','readonly')",date_input_from)
driver.execute_script("arguments[0].removeAttribute('readonly','readonly')",date_input_to)
date_input_from.clear()
date_input_to.clear()

date_input_from.send_keys("07/08/2024")
date_input_to.send_keys("07/08/2024")

search_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "searchBtn"))
)
search_button.click()

elements = driver.find_elements(By.CLASS_NAME, "lists")

header = [line.strip() for line in elements[0].text.split('\n')]
content = []

stop_processing = False

# Process content elements
for i in range(1, len(elements), 2):
    if stop_processing:
        break

    lines = [line.strip() for line in elements[i].text.split('\n')]
    
    # Check if the specific text is in lines
    if any("รายการที่" in line for line in lines):
        stop_processing = True
        continue

    item = {key: '' for key in header}

    for j, line in enumerate(lines):
        if j < len(header):
            key = header[j]
            if key in ["ถอน (บาท)", "ฝาก (บาท)"]:
                try:
                    value = float(line.replace(',', ''))
                    item["ถอน (บาท)"] = line if value < 0 else ''
                    item["ฝาก (บาท)"] = line if value >= 0 else ''
                except ValueError:
                    continue
            else:
                item[key] = line

    # Ensure only one of the fields has a value
    item["ฝาก (บาท)"] = item["ฝาก (บาท)"] or ''
    item["ถอน (บาท)"] = item["ถอน (บาท)"] or ''
    
    # Remove keys with empty values
    item = {k: v for k, v in item.items() if v}
    stop_processing = False
    content.append(item)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)
        print("Save to json file.")