import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
from bs4 import BeautifulSoup

webdriver_path = 'geckodriver'

def translate_query_to_url(query: str, timerange: str, region: str) -> str:
    base_url = 'https://sg.search.yahoo.com/search'
    params = {
        'q': query,
        'btf': timerange,
        'nojs': '1',
        'ei': 'UTF-8',
    }
    encoded_params = "&".join(f"{key}={value}" for key, value in params.items())
    url = f"{base_url}?{encoded_params}"
    return url

def extract_real_url(url):
    match = re.search(r'RU=([^/]+)', url)
    if match and match.group(1):
        return match.group(1)
    return url

def html_to_search_results(html, num_results):
    results = []
    soup = BeautifulSoup(html, 'html.parser')

    right_panel = soup.select('#right .searchRightTop')
    if right_panel:
        right_panel_link = right_panel[0].select('.compText a')[0]
        right_panel_info = right_panel[0].select('.compInfo li')
        right_panel_info_text = '\n'.join([el.get_text(strip=True) for el in right_panel_info])

        results.append({
    'title': right_panel_link.get_text(strip=True),
    'body': '\n\n'.join([f"{right_panel[0].select('.compText')[0].get_text(strip=True)}", right_panel_info_text]) if right_panel_info_text else right_panel[0].select('.compText')[0].get_text(strip=True),
    'url': extract_real_url(right_panel_link.get('href', '')),
})
    algo_sr = soup.select('.algo-sr:not([class*="ad"])')[:num_results]
    for el in algo_sr:
        title_element = el.select('h3.title a')[0]

        results.append({
            'title': title_element.get('aria-label', ''),
            'body': el.select('.compText')[0].get_text(strip=True),
            'url': extract_real_url(title_element.get('href', '')),
        })

    return results

def yahoosearch(num_results, query):
    url = translate_query_to_url(query,"","")
    results = html_to_search_results(requests.get(url).content, num_results)
    return results
    
    
print("Login to Open Assistant with your E-Mail with this link: https://open-assistant.io/auth/signin")
link = input("Copy the invite link from the email here (right click on sign in, copy link location): ")
def newchat(isinmenu=True):
    print("Starting new Chat...")
    if not isinmenu:
      driver.back()
    newchatbutton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div[1]/button")))
    newchatbutton.click()
    modelselect = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[text()='OA_SFT_Llama_30B_6']")))
    modelselect = modelselect.find_element(By.XPATH, "..")
    modelselect_select = Select(modelselect)
    modelselect_select.select_by_value("OA_RLHF_Llama_30B_2_7k")
    presetselect = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[text()='k50']")))
    presetselect = presetselect.find_element(By.XPATH, "..")
    presetselect_select = Select(presetselect)
    presetselect_select.select_by_value("k50-Precise")
print("Launching Firefox and opening Open Assistant...")
driver = webdriver.Firefox(executable_path=webdriver_path)
driver.minimize_window()
driver.get(link)
newchat()
while True:
    userprompt = input("Prompt (type \"newchat\" to start a new chat): ")
    if userprompt.lower() == "newchat":
       newchat(isinmenu=False)
       continue
    prompt = "Web search results\n\n "
    i=0
    for result in yahoosearch(3, userprompt):
       i+=1
       prompt+="["+str(i)+"]"+result["body"]+"\n\n"
    prompt+="Instructions: Using the provided web search results, write a comprehensive reply to the given query. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject.\n"
    prompt+="Query: "+userprompt
    promptfield = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div/textarea")
    promptfield.send_keys(prompt)
    sendbutton = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/form/div/div/button[2]")
    sendbutton.click()
    print("--------------")
    time.sleep(15)
    while True:
        driver.maximize_window()
        time.sleep(1)
        try:
           reply = driver.find_element(By.ID, "last_assistant_message")
           print(reply.text)
           print("--------------")
           driver.minimize_window()
           break
        except:
           pass
   

input("")
driver.implicitly_wait(5)
driver.quit()

