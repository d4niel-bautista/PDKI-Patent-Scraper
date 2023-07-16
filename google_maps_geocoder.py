import pandas as pd
import time
from tkinter import filedialog as fd
from tkinter import *
from tkinter import ttk
import os
import openpyxl
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

class GoogleMapsGeocoder():
    window = Tk()
    window_width = 400
    window_height = 500
    x = int(int(window.winfo_screenwidth()/2) - int(window_width/2))
    y = int(int(window.winfo_screenheight()/2) - int(window_height/2))
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    window.title("Geocoder")  # title of the GUI window
    window.resizable(False, False)
    tfr = Frame(window, width=400, height=10)
    tfr.grid(row=0, column=0, columnspan=2)
    title = Label(tfr, text="Geocoder", font=('Calibri', 32))
    title.grid(row=0, column=0, columnspan=2)
    ttk.Separator(
        master=tfr,
        orient=HORIZONTAL,
        class_= ttk.Separator,
        takefocus=1,
    ).grid(row=1, column=0, ipadx=150, pady=0, columnspan=2)
    dfr = Frame(window, width=400, height=10).grid(row=2, column=0, columnspan=2)
    desc_text = "1. Open the Excel file that needs geocoding.\n2. Enter the column name where the addresses are listed.\n3. Click Start!"
    desc = Label(dfr, text=desc_text, height=5, font=('Calibri', 11), wraplength=250, justify=LEFT)
    desc.grid(row=2, column=0, columnspan=2)
    ttk.Separator(
        master=dfr,
        orient=HORIZONTAL,
        class_= ttk.Separator,
        takefocus=1,    
    ).grid(row=3, column=0, ipadx=150, pady=6, columnspan=2)

    excel_file = ''
    column_name = ''
    space1 = Frame(master=window, height=35, width=50).grid(row=4, column=0, columnspan=2)
    open_button = ttk.Button(
    window,
    text='Open File')
    open_button.grid(row=5, column=0, ipadx=7, ipady=3, columnspan=2)
    filename = Label(text='', wraplength=250, height=3)
    filename.grid(row=6, column=0, columnspan=2)
    col_nm = Label(text="Column Name:")
    col_nm.grid(row=7, column=0, columnspan=2)
    col_inp = Entry(width=35)
    col_inp.grid(row=8, column=0, columnspan=2, ipady=3)
    col_inp.config(state=DISABLED)
    space2 = Frame(master=window, height=40, width=50).grid(row=9, column=0, columnspan=2)
    start = Button(width=6,text="Start")
    start.grid(row=10, column=0, columnspan=2, ipady=3)
    stop = Button(width=6,text="Stop")
    wait = Button(width=6,text="Wait...")
    start.config(state=DISABLED)
    status = Label(text="", pady=5)
    status.grid(row=11, column=0, columnspan=2)
    tracer = StringVar()

    browser = ''
    browser_path = "browser_path.txt"

    chromedriver = ChromeService(ChromeDriverManager().install())
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    option.add_argument("--headless")
    option.add_experimental_option("excludeSwitches", ["enable-logging"])

    event_obj = threading.Event()

    def select_file(self):
        filetypes = [
            ('Excel Files', '*.xlsx')]

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        if os.path.isfile(filename):
            self.filename.config(text=filename)
            self.col_inp.config(state=NORMAL)
            self.excel_file=filename
    
    def check_column(self, *args):
        val = self.tracer.get()
        if len(val) > 2: self.tracer.set(val[:70])
        if os.path.isfile(self.excel_file):
            columns = pd.read_excel(self.excel_file).columns
            if val not in columns:
                self.status.config(text="No column found!")
                self.start.config(state=DISABLED)
            else:
                self.start.config(state=ACTIVE)
                self.status.config(text="Column found!")
                self.column_name = val

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
    
    def driver_setup(self):
        driver = webdriver.Chrome(service=self.chromedriver, options=self.option)
        return driver

    def stop_geocode(self):
        self.stop.grid_forget()
        self.wait.grid(row=10, column=0, columnspan=2, ipady=3)
        self.event_obj.set()

    def geocode(self):
        self.start.grid_forget()
        self.stop.grid(row=10, column=0, columnspan=2, ipady=3)
        self.start.config(state=DISABLED)
        self.open_button.config(state=DISABLED)
        self.col_inp.config(state=DISABLED)
        self.status.config(text="Program is running!")
        df = pd.read_excel(self.excel_file, sheet_name=0, engine='openpyxl')
        coords_list = []
        driver = self.driver_setup()
        driver.get('https://www.google.com/maps/')
        action = ActionChains(driver)
        dim = driver.get_window_size()
        action.move_by_offset(((dim['width'] - 408)/2) + 412, dim['height']/2)
        wait = WebDriverWait(driver, 30)
        
        for i in range(df.shape[0]):
            address = str(df[self.column_name][i]).split(';')[0]
            buffer = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchboxinput"]')))
            search_bar = driver.find_element(By.XPATH, '//*[@id="searchboxinput"]')
            search_bar.clear()
            search_bar.send_keys(address)
            search_btn = driver.find_element(By.XPATH, '//*[@id="searchbox-searchbutton"]')
            search_btn.click()
            time.sleep(1.3)
            buffer_2 = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="minimap"]/div/div[2]/label')))
            
            action.context_click().perform()
            x = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="action-menu"]/div[1]')))
            coords = driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[1]')
            coords_list.append(coords.text)
            print(address + "\n" + coords.text + "\n")
        df['coordinates'] = coords_list
        df.to_excel(self.excel_file, index=False)
        self.start.config(state=ACTIVE)
        self.open_button.config(state=ACTIVE)
        self.col_inp.config(state=NORMAL)
        self.status.config(text="Program done!")
        self.wait.grid_forget()
        self.stop.grid_forget()
        self.start.grid(row=10, column=0, columnspan=2, ipady=3)
        self.event_obj.clear()
    
    def geocode_thread(self):
        t1 = threading.Thread(target=self.geocode)
        t1.start()

    def stop_thread(self):
        t2 = threading.Thread(target=self.stop_geocode)
        t2.start()
    
    def main(self):
        self.get_browser()
        self.option.binary_location = self.browser
        driver = webdriver.Chrome(service=self.chromedriver, options=self.option)
        self.tracer.trace_add('write', self.check_column)
        self.col_inp.config(textvariable=self.tracer)
        self.open_button.config(command=self.select_file)
        self.start.config(command=self.geocode_thread)
        self.stop.config(command=self.stop_thread)
        self.window.mainloop()

geocoder = GoogleMapsGeocoder()
geocoder.main()