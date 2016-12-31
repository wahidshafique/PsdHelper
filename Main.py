import socket
import os
from Tkinter import *
import Tkinter as tk
import Filler as filler
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

DESTURL = "http://localhost:8080/#/mSignup/user"
PORT = 8080

chromedriver = "chromedriver_win32/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)
driver.get(DESTURL)#the intial url


class Application(tk.Frame, object):
    def __init__(self, master=None):
        super(Application, self).__init__(master)
        w = Label(master, text="Choose Option")
        w.pack()
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.enter = tk.Button(self)
        self.enter["text"] = "\nRegister as Mentee\n goes up until signup"
        self.enter["command"] = self.registerMentee
        self.enter.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=lambda: sequence(root.destroy(), driver.quit()))
        self.quit.pack(side="bottom")

    def registerMentee(self):
        self.register()
        driver.implicitly_wait(2)
        driver.find_element_by_css_selector("div.card-container>a").click()

    def registerMentor(self):
        self.register()
        driver.find_element((By.XPATH, "//a[@href='#/mSignup/mentor-info']"))

    def register(self):
        displayName = driver.find_element_by_name("DisplayName")
        email = driver.find_element_by_name("email")
        password = driver.find_element_by_name("password")
        confPassword = driver.find_element_by_name("confirmPassword")

        displayName.send_keys(filler.textGenerator())

        EM = filler.textGenerator() + "@mail.com"
        email.send_keys(EM)
        PASS = filler.textGenerator()
        password.send_keys(PASS)
        confPassword.send_keys(PASS)

        driver.find_element_by_id("terms").click()
        driver.find_element_by_css_selector("button[ng-click*='SignUpUser']").click()#for angular

    def scrape(self):
        self.selectName()
        #retaining session id from base login (I think) , go to final url (the master appoint report)
        driver.get(DESTURL)
        select = Select(driver.find_element_by_name('rid'))
        select.select_by_value("sc57be02ac4a7d7")
        return


def sequence(*functions):
    def func(*args, **kwargs):
        return_value = None
        for function in functions:
            return_value = function(*args, **kwargs)
        return return_value
    return func

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = s.connect_ex(('127.0.0.1', PORT))

root = tk.Tk()
app = Application(master=root)
if result == 0:
    print('socket is open')
    app.mainloop()
sequence(driver.quit(), root.destroy())
print("no open port")