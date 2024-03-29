import socket
import os
from Tkinter import *
import Tkinter as tk
import tkMessageBox
import Filler as filler
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import httplib

#mongodb stuff, grab the db
client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.test
userProfiles = db.userprofiles
#endmongo stuff

PORT = 8080
DESTURL = "http://localhost:" + str(PORT) + "/#/mSignup/user"

chromedriver = "chromedriver_win32/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver

chromeOptions = webdriver.ChromeOptions()

driver = webdriver.Chrome(chromedriver, chrome_options=chromeOptions)
driver.get(DESTURL)#the intial url


class Application(tk.Frame, object):
    def __init__(self, master=None):
        self.username = "test"
        super(Application, self).__init__(master)
        w = Label(master, text="Choose Option")
        w.pack()
        self.pack(padx=20, pady=20)
        self.create_widgets()

    def create_widgets(self):
        self.regMentee = tk.Button(self, text="\nRegister as Mentee\n",
                  command=lambda: self.register_mentee()).pack(side="top")

        self.logMentee = tk.Button(self, text="\nLog in as Mentee\n",
                                   command=lambda: self.login("mentee@mail.com","password")).pack(side="top")

        self.regMentor = tk.Button(self, text="\nRegister as Mentor\n",
                  command=lambda: self.register_mentor()).pack(side="top", pady=(40, 0))

        self.logMentor = tk.Button(self, text="\nLog in as Mentor\n",
                                   command=lambda: self.login("mentor@mail.com", "password")).pack(side="top")

        self.removeAllProfiles = tk.Button(self, text="\n Remove all profiles",
                                           command=lambda:self.remove_prof())\

        self.removeAllProfiles.pack(side="top", pady=(40, 10))

        self.setAllProfiles = tk.Button(self, text="\n Set all profiles",
                                           command=lambda: self.set_prof())\

        self.setAllProfiles.pack(side="top", pady=(10, 10))

        tk.Button(self, text="RESET", fg="blue", command=lambda: reset()).pack(side="bottom")
        tk.Button(self, text="QUIT", fg="red",
                  command=lambda: filler.sequence(root.destroy(), driver.quit())).pack(side="bottom")

    def register_mentee(self):
        try:
            self.register()
            driver.implicitly_wait(2)#allows for dom to be loaded
            driver.find_element_by_name('signup-mentee').click()
            self.become_verified()
        except NoSuchElementException:
            print("element does not exist!")

    def register_mentor(self):
        try:
            self.register()
            driver.implicitly_wait(2)
            driver.find_element_by_name('signup-mentor').click()
            self.become_verified()
        except NoSuchElementException:
            print("element does not exist!")

    def register(self):
        displayName = driver.find_element_by_name("DisplayName")
        email = driver.find_element_by_name("email")
        password = driver.find_element_by_name("password")
        confPassword = driver.find_element_by_name("confirmPassword")

        self.username = filler.text_generator()
        displayName.send_keys(self.username)

        EM = filler.text_generator() + "@mail.com"
        email.send_keys(EM)
        PASS = filler.text_generator()
        password.send_keys(PASS)
        confPassword.send_keys(PASS)

        driver.find_element_by_id("terms").click()
        driver.find_element_by_css_selector("button[ng-click*='SignUpUser']").click()

    def login(self, EM, PASS):
        try:
            driver.find_element_by_css_selector("button[ng-click*='open']").click()
            #overlay takes precendent
            email = driver.find_element_by_name("email")
            email.send_keys(EM)

            password = driver.find_element_by_name("password")
            password.send_keys(PASS)
            driver.find_element_by_css_selector("button[ng-click*='login']").click()
        except (NoSuchElementException, ElementNotVisibleException):
            reset()

    def become_verified(self):
        userProfiles.update_one(
            {"username": self.username},
                {
                    "$set": {
                        "status": "verified"
                    }
                }
        )
        driver.refresh()
        driver.find_element_by_name("continue").click()
        driver.implicitly_wait(2)  # allows for dom to be loaded
        fill_form()

    def remove_prof(self):
        conn = httplib.HTTPConnection("localhost", PORT, timeout=10)
        conn.request("HEAD", "/set/removeProfiles")
        res = conn.getresponse()
        self.removeAllProfiles.config(state=DISABLED)
        self.setAllProfiles.config(state=NORMAL)
        print res.status, res.reason

    def set_prof(self):
        conn = httplib.HTTPConnection("localhost", PORT, timeout=10)
        conn.request("HEAD", "/set/alltest")
        res = conn.getresponse()
        self.setAllProfiles.config(state=DISABLED)
        self.removeAllProfiles.config(state=NORMAL)
        print res.status, res.reason

def fill_form():
    inputs = driver.find_elements_by_xpath("//form[@name='mentorshipForm']//input")
    print(inputs)
    for i in inputs:
        if i.is_displayed():
            i.send_keys("testing@mail.com")

    driver.find_element_by_xpath("//*[@id='background']/label[1]/span[1]").click()

    selects = driver.find_elements_by_xpath("//form[@name='mentorshipForm']//select")
    for sels in selects:
        sels.click()
        sels.send_keys(Keys.DOWN, Keys.RETURN)

    textAreas = driver.find_elements_by_xpath("//form[@name='mentorshipForm']//textarea")
    for t in textAreas:
        if t.is_displayed():
            t.send_keys(filler.text_generator(300))


def reset():
    if len(driver.find_elements_by_link_text('Logout')) > 0:
        driver.find_element_by_link_text('Logout').click()
    driver.get(DESTURL)
    print "reset"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = s.connect_ex(('127.0.0.1', PORT))

root = tk.Tk()
root.minsize(width=300, height=200)
root.wm_attributes("-topmost", 1)
app = Application(master=root)

if result == 0:
    print('socket is open')
    app.mainloop()
else:
    tkMessageBox.showerror(
        "Port Listener",
        "127.0.0.1:%i is not open \n did you start the server?" % PORT
    )
    filler.sequence(driver.quit(), root.destroy())
