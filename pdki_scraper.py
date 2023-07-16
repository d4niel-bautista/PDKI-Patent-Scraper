from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoSuchWindowException, InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from googletrans import Translator
import requests
import pandas as pd
import openpyxl
import time
import os
from bs4 import BeautifulSoup
import lxml
import re
import concurrent.futures
import numpy as np
import threading

class Scraper:
    chromedriver = ChromeService(ChromeDriverManager().install())
    browser = ''
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    option.add_argument("--headless")
    option.add_experimental_option("excludeSwitches", ["enable-logging"])
    translator = Translator()
    scrpt = ''
    event_obj = threading.Event()
    filename = 'indonesia_patents.xlsx'
    browser_path = "browser_path.txt"
    killTasks = False
    order = 'desc'
    page = 1
    max = 16
    columns = ['registered_date', 'title', 'abstract', 'inventor_name',
       'applicant_city', 'patent_id', 'utility_model_id',
       'industrial_design_id', 'geographic_indication_id', 'ipc_code',
       'industrial_design_classification', 'geographic_design_classification',
       'international_application_number', 'international_publication_number',
       'international_publication_date', 'international_filing_date',
       'priority_number(s)', 'priority_date(s)']

    def get_browser(self):
        if self.browser_path in os.listdir(".") and os.path.isfile(open(self.browser_path, 'r').readline()):
            with open(self.browser_path, 'r') as browser_tmp:
                self.browser = str(browser_tmp.readline())
        else:
            start = time.perf_counter()
            browsers = ['chrome.exe', 'brave.exe', 'msedge.exe']
            for browser in browsers:
                tmp = self.find_files(browser, 'C:\\')
                if os.path.isfile(tmp):
                    with open(self.browser_path, 'w+') as browser_tmp:
                        self.browser = tmp
                        browser_tmp.write(tmp)
                    end = time.perf_counter()
                    print("FOUND " + tmp + " " + str(end - start))
                    break
                else:
                    print(browser, "Not found")

    def find_files(self, filename, search_path):
        result = ''
        for root, dir, files in os.walk(search_path):
            if filename in files:
                temp = os.path.join(root, filename)
                if filename in temp.split('\\')[-1]:
                    result = temp
        return result

    def get_numbers_from_filename(self, filename):
        return re.search(r'\d+', filename).group(0)
    
    def add_number_to_filename(self):
        file_numbers = []
        for filename in os.listdir("."):
            if 'indonesia_patents' in filename:
                try:
                    file_numbers.append(int(self.get_numbers_from_filename(filename)))
                except:
                    continue
        excel_numbering = 0
        if len(file_numbers) != 0:
            excel_numbering = max(file_numbers)
        return excel_numbering

    patents_written = []

    def get_patents_written(self):
        if os.path.isfile(self.pid_index):
            with open(self.pid_index, 'r', encoding='utf-8') as p_idx:
                total_pids = p_idx.readlines()
                for i in total_pids:
                    self.patents_written.append(i.rstrip())
                
    def check_dupli(self):
        for file in os.listdir("."):
            if file.endswith(".xlsx"):
                excel_file = pd.read_excel(file, sheet_name=0, engine='openpyxl')
                if len(excel_file['international_application_number']) != 0:
                    for x in excel_file['international_application_number']:
                        if str(x) not in self.patents_written:
                            self.patents_written.append(str(x))
                        else:
                            print(x, "HAS DUPLICATE!")
        if len(self.patents_written) != 0:
            with open(self.pid_index, 'w+', encoding='utf-8') as f3:
                f3.writelines(str(ptnt) + "\n" for ptnt in self.patents_written)
            print("Patents found already written:", len(self.patents_written))
        else:
            print("Empty")
            open(self.pid_index, "w+").close()

    target_file = ''
    savefile = ''

    pid_index = 'pid_index' + str(scrpt) + '.txt'
    log_file = 'log' + str(scrpt) + '.txt'

    tmp_idx = []
    tmp_titles = []
    i = 0

    def driver_setup(self):
        driver = webdriver.Chrome(service=self.chromedriver, options=self.option)
        return driver

    #GET LINKS
    def get_links(self, chunk, driver):
        for page in chunk:
            if self.event_obj.is_set():
                print("Stopping Get links")
                break
            try:

                wait = WebDriverWait(driver, 30)
                print("PAGE", page)
                acs_start = time.perf_counter()
                indexer = 'https://pdki-indonesia.dgip.go.id/search?type=patent&page=' + str(page) + '&keyword=&order_column=tanggal_publikasi&order_state=' + self.order + '&status=Diberi'

                url_check = requests.get(indexer, verify=False)
                if(url_check.status_code != requests.codes['ok']):
                    continue
                acs_end = time.perf_counter()
                print("ACCESSING PAGE", str(page), str(acs_end-acs_start))
                get_start = time.perf_counter()
                driver.get(indexer)
                
                patents = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="text-sm text-gray-700"]')))

                indexer_body = driver.page_source
                soup = BeautifulSoup(indexer_body, 'lxml')

                patents = soup.find_all('div', class_='text-gray-800 font-semibold break-all hover:underline')

                # patents = [i for i in patents.get('href')]

                patents = [i.find('a')['href'] for i in patents]
  
                if len(patents) != 0:
                    get_end = time.perf_counter()
                    print("Page", str(page), "Starting writing to excel", str(get_end-get_start))
                    for link in patents:
                        self.write_to_excel(link, driver)
                
                driver.delete_all_cookies()
            except:
                print("Stopping getting links")
                break
    
    reg_date_excel = []
    title_excel = []
    abstract_excel = []
    inventors_excel = []
    address_excel = []
    patent_id_excel = []
    ipc_code_excel = []
    itl_app_num = []
    itl_pub_num = []
    itl_pub_date = []
    prio_dates = []
    prio_numbers = []

    def flush_lists(self):
        self.reg_date_excel.clear()
        self.title_excel.clear()
        self.abstract_excel.clear()
        self.inventors_excel.clear()
        self.address_excel.clear()
        self.patent_id_excel.clear()
        self.ipc_code_excel.clear()
        self.itl_app_num.clear()
        self.itl_pub_num.clear()
        self.itl_pub_date.clear()
        self.prio_dates.clear()
        self.prio_numbers.clear()
        self.patents_written.clear()

    workers = 4
    
    def setup_multiprocess(self, workers, func):
        active_workers = workers
        page_range = np.arange(self.page, self.max + 1)
        if len(page_range) < active_workers:
            active_workers = len(page_range)
        drivers = [self.driver_setup() for _ in range(int(active_workers))]
        chunks_list = np.array_split(page_range, int(active_workers))
        with concurrent.futures.ThreadPoolExecutor(max_workers=int(active_workers)) as executor:
            bucket = executor.map(func, chunks_list, drivers)
            # [print(item) for block in bucket for item in block]
        quit_start = time.perf_counter()
        [driver.quit() for driver in drivers]
        quit_end = time.perf_counter()
        print("Threads exited", str(quit_end - quit_start))

    def reset_threads(self):
        self.event_obj.clear()

    def write_to_excel(self, link, driver):
        if self.event_obj.is_set():
            print("Stopping Write to excel")
            return
        if link.split('nomor=')[1].split('?type=')[0] in self.patents_written:
            print('DUPLICATE! WILL SKIP', link + '\n')
            return
        start_time = time.perf_counter()
        pdki = 'https://pdki-indonesia.dgip.go.id' + link
        print(pdki)
        try:
            wait = WebDriverWait(driver, 30)
            driver.get(pdki)
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[1]/div[3]/div[2]/div/div[2]/div[1]/div[1]')))
            html_body = driver.page_source
            
            soup = BeautifulSoup(html_body, 'lxml')
            title = soup.find('div', class_='font-semibold text-gray-800 text-xl').text
            print(title)
            details = soup.find_all('div', class_='text-gray-800 font-semibold text-sm')

            announcement_date = details[1].text
            receipt_date = details[3].text

            if(receipt_date and announcement_date):
                rdate = receipt_date.split('-')[0]
                anndate = announcement_date.split('-')[0]
                if(((int(rdate)) < 2012) and (int(anndate) < 2012) or ((int(rdate)) is None) and (int(anndate) is None)):
                    with open(self.log_file, 'a+', encoding='utf-8') as v:
                        v.write('SKIPPED: ' + title  + '\n\n')
                        v.close()
                    print("SKIPPED:", title)
                    return

            pid = soup.find('div', class_='text-gray-800 font-semibold').text
            
            abstract = str(soup.find('div', class_='text-sm text-gray-800 leading-normal mt-1').text)
            
            ipc = [ip.text for ip in soup.find_all('div', class_='bg-navy text-white p-2 text-sm rounded') if ip != None]
            publication_num = "ID" + details[0].text

            tables = soup.find_all('table', class_='table-auto w-full')
            priority_table = tables[0].tbody.find_all('tr')
            priority_numbers = []
            priority_dates = []
            for pr in priority_table:
                priority_numbers.append(pr.find_all('td')[0].text)
                priority_dates.append(pr.find_all('td')[1].text)
            
            inventor_table = tables[2].tbody.find_all('tr')
            holder_table = tables[1].tbody.find_all('tr')
            inventors = []
            addresses = []
            for inv in inventor_table:
                inventors.append(inv.find_all('td')[0].text)
                addr = " ".join(inv.find_all('td')[1].text.replace('\n', ' ').split())
                if addr not in addresses:
                    if addr == '' or addr == '-' or addr == None:
                        for holdr_addr in holder_table:
                            hldr_add = " ".join(holdr_addr.find_all('td')[1].text.replace('\n', ' ').split())
                            if hldr_add not in addresses:
                                addresses.append(hldr_add)
                            else:
                                continue
                    else:
                        addresses.append(addr)
                else:
                    continue

            title_tl = ''
            abstract_tl = ''
            try:
                title_tl = self.translator.translate(str(title), src="id").text.upper()
            except:
                title_tl = title
            try:
                abstract_tl = self.translator.translate(str(abstract), src="id").text
            except:
                abstract_tl = abstract

            link = link.split('nomor=')[1].split('?type=')[0]

            self.reg_date_excel.append(str(receipt_date))
            self.title_excel.append(str(title_tl))
            self.abstract_excel.append(str(abstract_tl))
            self.inventors_excel.append(str(";".join(inventors)))
            self.address_excel.append(str(";".join(addresses)))
            self.patent_id_excel.append(str(pid))
            self.ipc_code_excel.append(str(";".join(ipc)))
            self.itl_app_num.append(str(link))
            self.itl_pub_num.append(str(publication_num))
            self.itl_pub_date.append(str(announcement_date))
            self.prio_dates.append(str(";".join(priority_dates)))
            self.prio_numbers.append(str(";".join(priority_numbers)))

            print('WRITING TO ' + self.savefile + '...')
            df = pd.DataFrame(columns=self.columns)
            df['registered_date'] = self.reg_date_excel
            df['title'] = self.title_excel
            df['abstract'] = self.abstract_excel
            df['inventor_name'] = self.inventors_excel
            df['applicant_city'] = self.address_excel
            df['patent_id'] = self.patent_id_excel
            df['ipc_code'] = self.ipc_code_excel
            df['international_application_number'] = self.itl_app_num
            df['international_publication_number'] = self.itl_pub_num
            df['international_publication_date'] = self.itl_pub_date
            df['priority_number(s)'] = self.prio_numbers
            df['priority_date(s)'] = self.prio_dates

            df.to_excel(self.savefile, index=False)
            
            self.patents_written.append(link)

            driver.delete_all_cookies()
            with open(self.pid_index, 'a+', encoding='utf-8') as f3:
                f3.write(str(link) + "\n")
            finish_time = time.perf_counter()
            print("DONE IN " + str(finish_time - start_time) + "!\n")
        except NoSuchElementException as e:
            print(e)
            with open(self.log_file, 'a+', encoding='utf-16') as f:
                f.write(str(e) + "\n")
                f.write(self.tmp_idx[link] + "\n")
                f.write(pdki + "\n\n")
            return
        except TimeoutException as e:
            print(e)
            return
        except InvalidSessionIdException as e:
            print(e)
            return
        except:
            return

    def end_scraper(self):
        self.event_obj.set()

    def run(self):
        self.get_browser()
        self.option.binary_location = self.browser
        self.flush_lists()
        self.check_dupli()
        added_num = self.add_number_to_filename()
        self.target_file = 'indonesia_patents' + str(added_num) +'.xlsx'
        self.savefile = 'indonesia_patents' + str(added_num + 1) +'.xlsx'
        self.get_patents_written()
        self.reset_threads()
        self.setup_multiprocess(self.workers, self.get_links)
        try:
            pass
        except:
            if self.killTasks:
                os.system('cmd /c "taskkill /F /IM "' + str(self.browser.split('\\')[-1]) + '" /T"')
            print("Ended!")
            return
        if self.killTasks:
            os.system('cmd /c "taskkill /F /IM "' + str(self.browser.split('\\')[-1]) + '" /T"')
        print("Done!")
        return


