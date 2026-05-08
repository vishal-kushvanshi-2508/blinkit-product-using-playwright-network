
import os
import zipfile
import zipfile
import json
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




def blinkit_product_detail_using_file():
    print("------------blinkit_product_detail_using_file----------------")

    # folder_path = r"D:\vishal_kushvanshi\play_wright_pages\blinkit_product_by_netwrok_reponse\blinkit_product_detail"
    # folder_path = r"D:\vishal_kushvanshi\play_wright_pages\blinkit_product_by_netwrok_reponse\blinkit_product_detail_second"
    # folder_path = r"D:\vishal_kushvanshi\play_wright_pages\blinkit_product_by_netwrok_reponse\blinkit_product_detail_third"
    folder_path = r"D:\vishal_kushvanshi\play_wright_pages\blinkit_product_by_netwrok_reponse\blinkit_product_detail_four"


    product_detail = []
    for file_name in os.listdir(folder_path):

        print("file_name : ", file_name)
        
        if file_name.endswith(".zip"):
            zip_file_path = os.path.join(folder_path, file_name)

            with zipfile.ZipFile(zip_file_path, "r") as zipf:
                with zipf.open("response.json") as file:
                    data = json.load(file)


            snippets_list = data.get("response", {}).get("snippets", [])
            if not snippets_list:
                print("not data found ... : ", zip_file_path)
                continue
            
            stock_status = snippets_list[2].get("tracking", {}).get("common_attributes", {}).get("state")
            
            for snippets_data in snippets_list:

                # if snippets_data.get("tracking", {}).get("common_attributes", {}):
                #     stock_status = snippets_data.get("tracking", {}).get("common_attributes", {}).get("state")

                if snippets_data.get("data", {}):
                    
                    for list_data in snippets_data.get("data", {}).get("rfc_actions_v2", {}).get("default", []):
                        if list_data.get("remove_from_cart", {}).get("cart_item", {}):
                            product_id = list_data.get("remove_from_cart", {}).get("cart_item", {}).get("product_id")
                            product_name = list_data.get("remove_from_cart", {}).get("cart_item", {}).get("product_name")   
                            quantity = list_data.get("remove_from_cart", {}).get("cart_item", {}).get("quantity")
                            product_price = list_data.get("remove_from_cart", {}).get("cart_item", {}).get("mrp")
                            unit = list_data.get("remove_from_cart", {}).get("cart_item", {}).get("unit")
                            image_url = list_data.get("remove_from_cart", {}).get("cart_item", {}).get("image_url")
                            
                            product_name_lower = format_name(product_name)
                            product_url = f"https://blinkit.com/prn/{product_name_lower}/prid/{product_id}"
                            
                            product_detail.append({
                                "product_id" : product_id,
                                "product_name" : product_name,
                                "product_url" : product_url,
                                "quantity" : quantity,
                                "product_price" : product_price,
                                "stock_status" : stock_status,
                                "unit" : unit,
                                "image_url" : image_url
                            })

    # insert data 
    insert_product_detail_table(list_data =product_detail)

