import socket
import os
from Tkinter import *
import Tkinter as tk
import Filler as filler
from selenium import webdriver
from pymongo import MongoClient

#mongodb stuff, grab the db
client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.test
userprofiles = db.userprofiles
#print userprofiles.find_one({"username": "yebfly"})
#endmongo stuff

DESTURL = "http://localhost:8080/#/mSignup/user"
PORT = 8080

chromedriver = "chromedriver_win32/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver
driver = webdriver.Chrome(chromedriver)
driver.get(DESTURL)#the intial url


class Application(tk.Frame, object):
    def __init__(self, master=None):
        self.username = "test"
        super(Application, self).__init__(master)
        w = Label(master, text="Choose Option")
        w.pack()
        self.pack(padx=20,pady=20)
        self.create_widgets()

    def create_widgets(self):
        self.regMentee =  tk.Button(self, text="\nRegister as Mentee\n",
                  command=lambda: self.register_mentee()).pack(side="top")

        self.regMentor = tk.Button(self, text="\nRegister as Mentor\n",
                  command=lambda: self.register_mentor()).pack(side="top")

        tk.Button(self, text="QUIT", fg="red",
                  command=lambda: sequence(root.destroy(), driver.quit())).pack(side="bottom")

    def register_mentee(self):
        self.register()
        driver.implicitly_wait(2)#allows for dom to be loaded
        driver.find_element_by_name('signup-mentee').click()
        self.become_verified()

    def register_mentor(self):
        self.register()
        driver.implicitly_wait(2)#allows for dom to be loaded
        driver.find_element_by_name('signup-mentor').click()
        self.become_verified()

    def register(self):
        displayName = driver.find_element_by_name("DisplayName")
        email = driver.find_element_by_name("email")
        password = driver.find_element_by_name("password")
        confPassword = driver.find_element_by_name("confirmPassword")

        self.username = filler.textGenerator()
        displayName.send_keys(self.username)

        EM = filler.textGenerator() + "@mail.com"
        email.send_keys(EM)
        PASS = filler.textGenerator()
        password.send_keys(PASS)
        confPassword.send_keys(PASS)

        driver.find_element_by_id("terms").click()
        driver.find_element_by_css_selector("button[ng-click*='SignUpUser']").click()#for angular

    def become_verified(self):
        userprofiles.update_one(
            {"username": self.username},
                {
                    "$set": {
                        "status": "verified"
                    }
                }
        )
        driver.refresh()
        driver.find_element_by_css_selector("a[ng-click*='AppendUserData']").click()


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
root.minsize(width=300, height=200)
app = Application(master=root)
if result == 0:
    print('socket is open')
    app.mainloop()
else: sequence(driver.quit(), root.destroy())
print("no open port")