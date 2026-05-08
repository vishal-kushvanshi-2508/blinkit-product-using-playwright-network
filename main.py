
from get_blinkit_response import *
import time
from store_data_database import *
from fetch_product_detail_response import *
from product_detail_using_file import *

def main():

    # # create table 
    # create_blinkit_product_url_table()

    # # ----------1 get main json response to find product url -----------
    # blinkit_capture_responses()

    # # # ----------2 fetch product url -----------
    # product_url_list = fetch_blinkit_product_url_table()
    # # print(product_url_list)
    # print("product_url_list : ",len(product_url_list))

    # run_url_thread_wise(product_url_list)

    # ----------3 fetch product detail by file -----------

    # create table 
    create_product_detail_table()

    blinkit_product_detail_using_file()











if __name__ == "__main__":
    start_time = time.time()
    main()
    print("time difference  : ", time.time() - start_time)

