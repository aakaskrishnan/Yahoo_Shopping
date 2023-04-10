import sys
import time
import csv
import numpy as np
import zipfile
import config
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from proxy_setup import manifest_json, get_background_js

class yahooscraper:


    def __init__(self):
        self.main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

    def short_sleep(self):
        time.sleep(np.random.randint(2,3))

    def link_search(self,driver,link,dict):
        self.driver = driver
        self.link = link
        self.dict = dict
        driver.get(link)
        short_sleep = self.short_sleep()
        SKU = driver.find_element(By.XPATH, "//dd[@class='elName']").text
        Store = driver.find_element(By.XPATH, "//dd[@class='elStore']").text
        Price = driver.find_element(By.XPATH, "//dd[@class='elPrice']").text
        Product_Rating = driver.find_element(By.XPATH, "//dd[@class='elReviewAverage']").text
        Review_Count = driver.find_element(By.XPATH, "//dd[@class='elReviewTotalCount']").text
        dict = self.fetch_reviews(driver,dict)
        for x in dict:
            x["_root"],x["Source"],x["SKU"],x["Price"],x["Product_Rating"],x["Review_Count"]=link,"Yahoo",SKU,Price,Product_Rating,Review_Count
        return dict

    def fetch_reviews(self,driver,dict):
        #short_sleep = self.short_sleep()
        elements = driver.find_elements(By.XPATH, "//li[@class='elItem isOther']")
        #short_sleep = self.short_sleep()
        for element in elements:
            Review = element.find_element(By.XPATH, "div[@class='elItemComment']/p[@class='elItemCommentText']").text
            Author = element.find_element(By.XPATH,"div[@class='elItemUser']/div[@class='elItemPersonal']/p[@class='elItemUserName']").text
            Review_Rating = element.find_element(By.XPATH, "p[@class='elItemScore']").text
            date = element.find_element(By.XPATH, "div[@class='elItemTop']/p[@class='elItemDate']").text
            Title = element.find_element(By.XPATH, "div[@class='elItemTop']/p[@class='elItemCommentTitle']").text
            dict.append({"Review":Review,"Review_Rating":Review_Rating,"date":date,"Author":Author})
        self.pagination(driver,dict)
        return dict

    def pagination(self,driver,dict):
        try:
            pagination_link = driver.find_element(By.XPATH, "//div[@class='mdMoreButton']/p[@class='elMoreButton']/button")
            ActionChains(driver).click(pagination_link).perform()
            #short_sleep = self.short_sleep()
            driver.localStorage.clear()
            #driver.manage().deleteAllCookies();
            self.fetch_reviews(driver,dict)
        except:
            pass

    def remove_duplicate_dict(self,dict):
        self.dict = dict
        deduplicated_list = []
        for i in range(len(dict)):
            if dict[i] not in dict[i+1:]:
                deduplicated_list.append(dict[i])
        return deduplicated_list

    def read_csv(self,input_file_path):
        row_list = []
        with open(input_file_path, 'r', newline="") as bf:
            csvf = csv.DictReader(bf, delimiter=',', quotechar='"')
            field_names = csvf.fieldnames
            for row in csvf:
                row_list.append(row)
            return row_list, field_names

    def write_csv(self,output_file_path, final_dataset):
        field_names = ["Review","Review_Rating","date","Author","_root","Source","SKU","Price","Product_Rating","Review_Count"]
        with open(output_file_path, 'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=field_names, delimiter=',', quotechar='"')
            writer.writeheader()
            for rows in final_dataset:
                for row in rows:
                    writer.writerow(row)

    def get_driver(self,proxy_username: str, proxy_password: str, debug=True):
        options = Options()
        options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-notifications")
        options.add_argument('--no-sandbox')
        options.add_argument("--lang=en")
        pluginfile = 'proxy_auth_plugin.zip'
        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", get_background_js(username=proxy_username, password=proxy_password))
        options.add_extension(pluginfile)
        input_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        return input_driver

    def main(self,proxy,password,input_links_path,output_file_path):
        driver = self.get_driver(proxy,password)
        row_list, _ = self.read_csv(input_links_path)
        end_result=list()
        dict = []
        for row in row_list:
            link = row['link']
            result_1 = self.link_search(driver, link,dict)
            result = self.remove_duplicate_dict(result_1)
            end_result.append(result)
            print(type(end_result))
        self.write_csv(output_file_path, end_result)


crawler = yahooscraper()
crawler