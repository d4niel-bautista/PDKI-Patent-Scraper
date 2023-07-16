# import tkinter module
from tkinter import *
from tkinter import ttk
import pdki_scraper as rf
from threading import *
 
# creating main tkinter window/toplevel
class ScrprGUI():
    class Prox(ttk.Entry):
        '''A Entry widget that only accepts digits'''
        def __init__(self, master=None, **kwargs):
            self.var = StringVar(master)
            self.var.trace('w', self.validate)
            ttk.Entry.__init__(self, master, textvariable=self.var, **kwargs)
            self.get, self.set = self.var.get, self.var.set
        def validate(self, *args):
            value = self.get()
            if not value.isdigit():
                self.set(''.join(x for x in value if x.isdigit()))
            self.set(self.get().lstrip('0'))
            if self.get().isdigit():
                if int(self.get()) > 1000:
                    self.set(1000)
        def val_workers(self, *args):
            value = self.get()
            if not value.isdigit():
                self.set(''.join(x for x in value if x.isdigit()))
            self.set(self.get().lstrip('0'))
            if self.get().isdigit():
                if int(self.get()) > 16:
                    self.set(16)
    scraper = rf.Scraper()
    window = Tk()
    window_width = 600
    window_height = 600
    x = int(int(window.winfo_screenwidth()/2) - int(window_width/2))
    y = int(int(window.winfo_screenheight()/2) - int(window_height/2))
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    window.title("Indonesia Patent Scraper")  # title of the GUI window
    window.resizable(False, False)
    event_obj = Event()

    tfr = Frame(window, width=600, height=10)
    tfr.grid(row=0, column=0, columnspan=2)
    title = Label(tfr, text="Indonesia Patent Scraper", font=('Calibri', 32))
    title.grid(row=0, column=0, columnspan=2)
    ttk.Separator(
        master=tfr,
        orient=HORIZONTAL,
        class_= ttk.Separator,
        takefocus=1,
    ).grid(row=1, column=0, ipadx=250, pady=0, columnspan=2)
    dfr = Frame(window, width=600, height=10).grid(row=2, column=0, columnspan=2)
    desc_text = "This program will scrape patents from PDKI: https://pdki-indonesia.dgip.go.id/ that have publication or application year 2012 and above. This program is made in order to help data extraction for patents in CHED GIA Project."
    desc = Label(dfr, text=desc_text, height=10, font=('Calibri', 11), wraplength=400, justify=LEFT)
    desc.grid(row=2, column=0, columnspan=2)
    ttk.Separator(
        master=dfr,
        orient=HORIZONTAL,
        class_= ttk.Separator,
        takefocus=1,    
    ).grid(row=3, column=0, ipadx=250, pady=6, columnspan=2)

    def on_enter_pages(self, e):
        self.desc['text'] = "SETTING THE PAGES TO SCRAPE:\nThis option is to set the pages you want to scrape. This will only extract the patents within the page range found in the website.\nDefault first page is 1\nMax page is 1000"
    
    def on_enter_order(self, e):
        self.desc['text'] = "ASCENDING OR DESCENDING:\nThis option will set the ordering of the patents listed in the PDKI website.\nIf newest to oldest: Descending\nIf oldest to newest: Ascending"
    
    def on_enter_workers(self, e):
        self.desc['text'] = "THREADING:\nThis will set the number of threads(workers) that will work simultaneously in extracting data from the website. If the page range specified is lower than the threads, the number of active threads will be adjusted.\nMax Threads: 16"
    
    def on_enter_taskkill(self, e):
        self.desc['text'] = "MEMORY MANAGEMENT:\nThis option will terminate background processes in order to free up memory. Some background processes of the browser used by the threads might still be taking up space in the computer's memory even after the scraper ended, this option will clear the processes left.\nOnly consider enabling this option if you experience committed memory build-up. You can check this by opening Task Manager and going to Performance tab.\nNOTE: When enabled, this will also kill any browsers open!"
    
    def on_leave(self, e):
        self.desc['text'] = self.desc_text

    options = Label(window, text="Options:", font=('Calibri', 11))
    options.grid(row=4, column=0, sticky="w", padx=70)
    set_pages = Label(window, text="Set Pages:", font=('Calibri', 11))
    set_pages.grid(row=7, column=0, sticky="w", padx=70)
    set_threads = Label(window, text="Threading:", font=('Calibri', 11))
    set_threads.grid(row=10, column=0, sticky="w", padx=70)
    set_taskkill = Label(window, text="Memory Management:", font=('Calibri', 11))
    set_taskkill.grid(row=12, column=0, sticky="w", padx=70)

    taskkill_val = IntVar()
    radio = IntVar()

    def select_order(self):
        if self.radio.get() == 1:
            self.scraper.order = "desc"
        elif self.radio.get() == 2:
            self.scraper.order = "asc"
    
    def check_taskkill(self):
        if self.taskkill_val.get() == 1:
            self.scraper.killTasks = True
        else:
            self.scraper.killTasks = False

    def stop(self):
        self.scraper.end_scraper()

    def stop_threads(self):
        workers = list()
        for worker in range(self.scraper.workers):
            x = Thread(target=self.stop)
            workers.append(x)
            x.start()
        self.stopbtn.grid_forget()
        self.loadingbtn.grid(row = 20, columnspan=2)
    
    def start_thread(self):
        self.start.grid_forget()
        self.scraper.page = int(self.page.get())
        self.scraper.max = int(self.max_page.get())
        self.scraper.workers = int(self.workers.get())
        self.workers.config(state=DISABLED)
        self.desc_order.config(state=DISABLED)
        self.asc_order.config(state=DISABLED)
        self.page.config(state=DISABLED)
        self.max_page.config(state=DISABLED)
        self.taskkill.config(state=DISABLED)
        t1=Thread(target=self.run_scraper)
        t1.start()
        self.stopbtn.grid(row = 20, columnspan=2)

    def run_scraper(self):
        self.scraper.run()
        self.stopbtn.grid_forget()
        self.loadingbtn.grid_forget()
        self.start.grid(row = 20, columnspan=2)
        self.workers.config(state=ACTIVE)
        self.desc_order.config(state=ACTIVE)
        self.asc_order.config(state=ACTIVE)
        self.page.config(state=ACTIVE)
        self.max_page.config(state=ACTIVE)
        self.taskkill.config(state=ACTIVE)

    def check_pages(self, e):
        if len(self.page.get()) == 0:
            self.page.set(1)
        if len(self.workers.get()) == 0:
            self.workers.set(4)
        if len(self.max_page.get()) == 0:
            self.max_page.set(1)
        if int(self.page.get()) > int(self.max_page.get()):
            self.page.set(int(self.max_page.get()))
        self.window.focus()

    start = Button(window, text="Start", width=6)
    start.grid(row = 20, columnspan=2)
    stopbtn = Button(window, text="Stop", width=6)
    loadingbtn = Button(window, text="Wait...", width=6)
    page = Prox(width=6)
    max_page = Prox(width=6)
    workers = Prox(width=3)
    desc_order = Radiobutton(window, text="Descending", variable=radio, value=1)
    asc_order = Radiobutton(window, text="Ascending", variable=radio, value=2)
    taskkill = Checkbutton(window, text="Kill Tasks", variable=taskkill_val, onvalue=1)
    
    def main(self):
        self.desc_order.grid(row = 5, column=0, sticky="w", padx=100)
        self.asc_order.grid(row = 6, column=0, sticky="w", padx=100)
        self.desc_order.config(command=self.select_order)
        self.asc_order.config(command=self.select_order)
        self.taskkill.config(command=self.check_taskkill)
        self.desc_order.select()
        set_page = Label(self.window, text="First page:")
        set_max = Label(self.window, text="Last page:")
        set_workers = Label(self.window, text="Threads:")
        set_workers.grid(row=11, column=0, sticky="w", padx=100)
        set_page.grid(row = 8, column=0, sticky="w", padx=100)
        set_max.grid(row = 9, column=0, sticky="w", padx=100)
        self.workers.grid(row = 11, column=0, sticky="w", padx=165)
        self.workers.var.trace('w', self.workers.val_workers)
        self.taskkill.grid(row = 13, column=0, sticky="w", padx=100)
        
        self.page.grid(row = 8, column=0, sticky="w", padx=165)
        self.max_page.grid(row = 9, column=0, sticky="w", padx=165)
        self.start.config(command=self.start_thread)
        self.stopbtn.config(command=self.stop_threads)

        self.window.bind("<FocusOut>", self.check_pages)
        self.desc_order.bind("<Button-1>", self.check_pages)
        self.asc_order.bind("<Button-1>", self.check_pages)
        self.taskkill.bind("<Button-1>", self.check_pages)
        self.options.bind("<Enter>", self.on_enter_order)
        self.desc_order.bind("<Enter>", self.on_enter_order)
        self.asc_order.bind("<Enter>", self.on_enter_order)
        self.options.bind("<Leave>", self.on_leave)
        self.desc_order.bind("<Leave>", self.on_leave)
        self.asc_order.bind("<Leave>", self.on_leave)
        self.page.bind("<Enter>", self.on_enter_pages)
        self.max_page.bind("<Enter>", self.on_enter_pages)
        set_page.bind("<Enter>", self.on_enter_pages)
        set_max.bind("<Enter>", self.on_enter_pages)
        self.set_pages.bind("<Enter>", self.on_enter_pages)
        self.page.bind("<Leave>", self.on_leave)
        self.max_page.bind("<Leave>", self.on_leave)
        set_page.bind("<Leave>", self.on_leave)
        set_max.bind("<Leave>", self.on_leave)
        self.set_pages.bind("<Leave>", self.on_leave)
        self.workers.bind("<Enter>", self.on_enter_workers)
        self.workers.bind("<Leave>", self.on_leave)
        self.set_threads.bind("<Enter>", self.on_enter_workers)
        self.set_threads.bind("<Leave>", self.on_leave)
        set_workers.bind("<Enter>", self.on_enter_workers)
        set_workers.bind("<Leave>", self.on_leave)
        self.taskkill.bind("<Enter>", self.on_enter_taskkill)
        self.taskkill.bind("<Leave>", self.on_leave)
        self.set_taskkill.bind("<Enter>", self.on_enter_taskkill)
        self.set_taskkill.bind("<Leave>", self.on_leave)
        self.workers.set(4)
        self.page.set(1)
        self.max_page.set(16)

        self.window.mainloop()

def main():
    scraper = ScrprGUI()
    scraper.main()

main()                                                                 