


from playwright.sync_api import sync_playwright
import json
import os
import zipfile
from store_data_database import *

import re

def format_name(name):
    # convert to lowercase
    name = name.lower()
    
    # replace spaces & special chars with hyphen
    name = re.sub(r'[^a-z0-9]+', '-', name)
    
    # remove extra hyphens
    name = name.strip('-')
    
    return name



def make_product_url(product_data):
    print("-----------make_product_url---------------")

    results = []
    for object in product_data.get("objects"):

        if object.get("header_config", {}):
            category_name = object.get("header_config", {}).get("title")

            single_object = []
            if object.get("objects", []):
                single_object =  object.get("objects", [])[0]
            else:
                continue
            

            for product_list  in single_object.get("data", {}).get("products", []):
                

                for item in product_list :

                    product_name = item.get("group_name")
                    product_id = item.get("default_product_id")

                    if not product_name or not product_id:
                        continue

                    formatted_name = format_name(product_name)

                    product_url = f"https://blinkit.com/prn/{formatted_name}/prid/{product_id}"

                    results.append({
                        "category_name" : category_name,
                        "product_id": product_id,
                        "product_name": product_name,
                        "product_url": product_url,
                        "status" : "pending"
                    })

    # insert data 
    insert_blinkit_product_url_table(list_data =results)



def blinkit_capture_responses():


    # create folder for html if not exists
    folder_path = r"D:\vishal_kushvanshi\play_wright_pages\blinkit_product_by_netwrok_reponse"
    os.makedirs(f"{folder_path}\\blinkit_caterory", exist_ok=True)

    location_selected = False   #  NEW FLAG
    saved = False               #  STOP AFTER FIRST FULL DATA

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def handle_response(response):

            nonlocal location_selected, saved   #  VERY IMPORTANT

            #  Ignore BEFORE location is set
            if not location_selected or saved:
                return
        
            try:
                url = response.url
                rtype = response.request.resource_type

                # SPECIAL CASE: Flipkart main page
                if (
                    "https://blinkit.com/feed/?template_version=9" == url
                    and rtype == "fetch"
                ):
                    try:
                        print("store response in file response url : ", url)
                        data = response.json()

                        zip_file_name = f"{folder_path}\\blinkit_caterory\\main_page_response.zip"
                        with zipfile.ZipFile(zip_file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
                            zipf.writestr("main_page_product_response.json", json.dumps(data, indent=4))

                        # ---------call make_product_url to make product url---------------
                        make_product_url(data)

                        print(" blinkit HTML saved")
                        saved = True   #  STOP further processing

                    except Exception as e:
                        print("HTML save error:", e)

            except Exception as e:
                print("Error:", e)

        # attach before navigation
        page.on("response", handle_response)

        page.goto("https://blinkit.com/", wait_until="load")


        #  Step 2: Close popup (VERY IMPORTANT)
        try:

            # 1️ Wait for popup input field
            page.wait_for_selector('xpath=//input[contains(@placeholder,"search delivery location")]', timeout=10000)
            print("Title:", page.title())


            # 2️ Click input (IMPORTANT)
            search_box = page.locator('xpath=//input[contains(@placeholder,"search delivery location")]')
            search_box.click()

            # 3️ Type pincode
            search_box.fill("382405")

            # 4️ Wait for suggestion to appear
            page.wait_for_selector(
                'xpath=(//div[@class="address-container-v1"]//div[@class="LocationSearchList__LocationDetailContainer-sc-93rfr7-1 bBiSUM"])[1]', 
                timeout=10000)

            # 5️ Click the location suggestion
            page.locator(
                'xpath=(//div[@class="address-container-v1"]//div[@class="LocationSearchList__LocationDetailContainer-sc-93rfr7-1 bBiSUM"])[1]'
            ).click()

            print(" choose location ")

            location_selected = True   #  VERY IMPORTANT
        except:
            print(" choose location not found")

        page.wait_for_timeout(8000)

        browser.close()

    print(" Metadata saved in responses.json")

    