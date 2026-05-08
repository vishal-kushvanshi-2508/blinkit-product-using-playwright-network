


from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import os
import zipfile
from store_data_database import *
import gzip



def attach_handler(page, id,  product_id, search_response_url, folder_path):
    saved = False  #  now per-tab

    def handle_response(response):
        nonlocal saved
        if saved:
            return
        try:
            url = response.url
            rtype = response.request.resource_type
            # print("product url : ", url, rtype)
            if search_response_url in url and rtype == "fetch":

                # time.sleep(15)
                data = response.json()
                zip_file = f"{folder_path}\\product_page_{product_id}.zip"

                with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.writestr("response.json", json.dumps(data, indent=4))

                saved = True

                # update status 
                update_blinkit_product_url_status(id, "success")

        except Exception as e:
            print("Error:", e)

    page.on("response", handle_response)

def multi_browser_in_multi_tab(chunk, max_tab=5):
    print("chunk lenght : ", len(chunk) )

    # create folder for html if not exists
    folder_path = r"D:\vishal_kushvanshi\play_wright_pages\blinkit_product_by_netwrok_reponse\blinkit_product_detail_four"
    os.makedirs(f"{folder_path}", exist_ok=True)

    with sync_playwright() as f:
        browser = f.chromium.launch(headless=False)
        new_cotext = browser.new_context()
        pages = [ new_cotext.new_page()  for i in range(max_tab)]

        for i in range(0, len(chunk), max_tab):
            batch = chunk[i:i+max_tab]
            
            for index, data in enumerate(batch):
                id = str(data.get("id"))
                product_id = str(data.get("product_id"))
                search_response_url = "https://blinkit.com/v1/layout/product/" + product_id
                product_url = data.get("product_url")

                page = pages[index]

                #  attach handler with unique values
                attach_handler(page, id, product_id, search_response_url, folder_path)

                # retry condition
                for attempt in range(3):
                    try:
                        page.goto(product_url, timeout=120000, wait_until="load")
                        break
                    except Exception as e:
                        print(f"Retry {attempt+1} failed:", e)
                        page.wait_for_timeout(2000)


                print("open car url : ", id ," ",  product_id,  product_url, ", now : ", search_response_url)        

        browser.close()



def data_into_chunk(car_url_list, chunk_size):
    for i in range(0, len(car_url_list), chunk_size):
        yield car_url_list[i:i+chunk_size]


def run_url_thread_wise(car_url_list, max_thread=5):
    print("----------run_url_thread_wise-----------------")

    chunk_size = ( len(car_url_list) // max_thread ) + 1


    chunk_data = list(data_into_chunk(car_url_list, chunk_size))

    with ThreadPoolExecutor(max_workers=max_thread) as executer:
        futures = [
            executer.submit(multi_browser_in_multi_tab, chunk)
            for chunk in chunk_data
        ]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print("Thread error:", e)
    print("process done....")












#----------method 2 to set location and then find product data (but some bug not process all url )------------------

# from playwright.sync_api import sync_playwright
# from concurrent.futures import ThreadPoolExecutor, as_completed
# import time
# import json
# import os
# import zipfile
# from store_data_database import *
# import gzip



# def attach_handler(page, state, id,  product_id, search_response_url, folder_path):
#     saved = False  #  now per-tab

#     def handle_response(response):
#         nonlocal saved
#         if saved or not state["location_selected"]:
#             return
#         try:
#             url = response.url
#             rtype = response.request.resource_type
#             # print("product url : ", url, rtype)
#             if search_response_url in url and rtype == "fetch":

#                 # time.sleep(15)
#                 data = response.json()
#                 zip_file = f"{folder_path}\\product_page_{product_id}.zip"

#                 with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
#                     zipf.writestr("response.json", json.dumps(data, indent=4))
                
#                 # print("search_response_url : ", search_response_url, rtype, zip_file)


#                 saved = True
#                 # IMPORTANT
#                 state["response_saved"] = True

#                 # update status 
#                 update_blinkit_product_url_status(id, "success")

#         except Exception as e:
#             print("Error:", e)

#     page.on("response", handle_response)

# def multi_browser_in_multi_tab(chunk, max_tab=5):
#     print("chunk lenght : ", len(chunk) )

#     # create folder for html if not exists
#     folder_path = r"D:\vishal_kushvanshi\play_wright_pages\blinkit_product_by_netwrok_reponse\blinkit_product_detail_four"
#     os.makedirs(f"{folder_path}", exist_ok=True)

#     with sync_playwright() as f:
#         browser = f.chromium.launch(headless=False)
#         new_cotext = browser.new_context()
#         pages = [ new_cotext.new_page()  for i in range(max_tab)]

#         for i in range(0, len(chunk), max_tab):
#             batch = chunk[i:i+max_tab]
            
#             for index, data in enumerate(batch):
#                 id = str(data.get("id"))
#                 product_id = str(data.get("product_id"))
#                 search_response_url = "https://blinkit.com/v1/layout/product/" + product_id
#                 product_url = data.get("product_url")

#                 page = pages[index]

#                 # location_selected = False

#                 state = {"location_selected": False, "response_saved": False}

#                 #  attach handler with unique values
#                 attach_handler(page, state, id, product_id, search_response_url, folder_path)

#                 # retry condition
#                 for attempt in range(3):
#                     try:
#                         page.goto(product_url, timeout=120000, wait_until="load")

#                         #  Step 2: Close popup (VERY IMPORTANT)
#                         try:

#                             page.locator("//div[@class='LocationBar__Subtitle-sc-x8ezho-10 bdWwbr']").click()
#                             # 1️ Wait for popup input field
#                             page.wait_for_selector('xpath=//input[contains(@placeholder,"search delivery location")]', timeout=10000)
#                             # print("Title:", page.title())


#                             # 2️ Click input (IMPORTANT)
#                             search_box = page.locator('xpath=//input[contains(@placeholder,"search delivery location")]')
#                             search_box.click()

#                             # 3️ Type pincode
#                             search_box.fill("382405")

#                             # 4️ Wait for suggestion to appear
#                             page.wait_for_selector(
#                                 'xpath=(//div[@class="address-container-v1"]//div[@class="LocationSearchList__LocationDetailContainer-sc-93rfr7-1 bBiSUM"])[1]', 
#                                 timeout=10000)

#                             # 5️ Click the location suggestion
#                             page.locator(
#                                 'xpath=(//div[@class="address-container-v1"]//div[@class="LocationSearchList__LocationDetailContainer-sc-93rfr7-1 bBiSUM"])[1]'
#                             ).click()

#                             # print(" choose location ")
#                             # time.sleep(6)


#                             state["location_selected"] = True   #  VERY IMPORTANT

#                             for _ in range(30):

#                                 if state["response_saved"]:
#                                     print("Response Saved Successfully")
#                                     break

#                                 time.sleep(1)
                        
#                         except Exception as e :
#                             print("error show : ", e)


#                         break
#                     except Exception as e:
#                         print(f"Retry {attempt+1} failed:", e)
#                         page.wait_for_timeout(2000)


#                 print("open car url : ", id ," ",  product_id,  product_url, ", now : ", search_response_url)        
#         # time.sleep(5)
#         browser.close()


# def data_into_chunk(car_url_list, chunk_size):
#     for i in range(0, len(car_url_list), chunk_size):
#         yield car_url_list[i:i+chunk_size]


# def run_url_thread_wise(car_url_list, max_thread=5):
#     print("----------run_url_thread_wise-----------------")

#     chunk_size = ( len(car_url_list) // max_thread ) + 1


#     chunk_data = list(data_into_chunk(car_url_list, chunk_size))

#     with ThreadPoolExecutor(max_workers=max_thread) as executer:
#         futures = [
#             executer.submit(multi_browser_in_multi_tab, chunk)
#             for chunk in chunk_data
#         ]

#         for future in as_completed(futures):
#             try:
#                 future.result()
#             except Exception as e:
#                 print("Thread error:", e)
#     print("process done....")













