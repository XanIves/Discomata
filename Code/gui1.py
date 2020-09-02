#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 10:27:51 2019

Example use of tkinter with python threading.

@author: Benedict Wilkins AI & Alexander G. Ives
"""

import asyncio, discord, os, time
import tkinter as tk
from tkinter import ttk
from threading import Thread

from dotenv import load_dotenv
load_dotenv()   #Load discord keys and codes from .env file

# My variables
global message #This will serve as the queue for my_background_task to check and read from. When value is "empty", loop skips posting message
message = "empty"
client = discord.Client()

# Create a list to store user-inputted button templates
global userButtons
userButtons = []

# Discord syncing stuff
async def my_background_task():
    global message
    await client.wait_until_ready() # ensures cache is loaded
    counter = 0
    channel = client.get_channel(id=748651797350187139) # replace with target channel id
    while not client.is_closed():
        counter += 1
        if message != "empty":
            sentMessage = await channel.send(message)
            #await sentMessage.delete()  # deletes the original command posted to keep the chat clean
            message = "empty"
        await asyncio.sleep(1)  # or 300 if you wish for it to be 5 minutes

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #await channel.send("!beyond https://ddb.ac/characters/28780677/kdQS4u")
    client.loop.create_task(my_background_task()) # best to put it in here


class Sleep:

    def __init__(self, wait):
        self.wait = wait

    def __enter__(self):
        self.start = self.__t()
        self.finish = self.start + self.wait

    def __exit__(self, type, value, traceback):
        while self.__t() < self.finish:
            time.sleep(1./1000.)

    def __t(self):
        return int(round(time.time() * 1000))


def after(t, fun, *args):
    global finish
    if not finish:
        root.after(t, fun, *args)

def run():
    token = os.environ.get("DISCORD_TOKEN")
    print("Discord Token: " + token)
    client.run(token)

def avrae_command(command):
    # This function will take in command and enter it into discord as a text post.
    global message
    if command!=None and command!="empty":
        print("Button was pressed: " + command)
        message = command
    else:
        print("Error: empty command issued.")

def add_user_command(name, command):
    global userButtons
    userButtons.append(tk.Button(canvas, text=name, command = lambda: avrae_command(command)))
    for index, button in enumerate(userButtons):
        button.grid(column=1, row=index, sticky="WENS", padx=10, pady=2)

def quit():
    global finish
    finish = True
    root.destroy()


######## GUI ########

# Root Window. Contains the Left Window and the Right Window
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit)
root.title("Python Tkinter Text Box")
root.minsize(200,50)
root.configure(background='light blue')

# Left Window. Contains buttons for adding commands
subWindow = tk.LabelFrame(root,bd=1,bg='light blue', height=200, text=" Add New Command ", relief="ridge")
subWindow.pack(fill="y", side="left")

buttonNameEntry = tk.Entry(subWindow)       # Entry field for adding a new command's name
buttonNameEntry.grid(column=1,row=0)
buttonNameTitle = tk.Label(subWindow, text="Command Name",bg='light blue')
buttonNameTitle.grid(column=0,row=0, sticky="WS")

buttonCommandEntry = tk.Entry(subWindow)    # Entry field for adding a new command's text to be executed
buttonCommandEntry.grid(column=1,row=1)
buttonCommandTitle = tk.Label(subWindow, text="Command Text",bg='light blue')
buttonCommandTitle.grid(column=0,row=1, sticky="WS")

addButtonButton = tk.Button(subWindow, text="Add", command = lambda: add_user_command(buttonNameEntry.get(), buttonCommandEntry.get()))
addButtonButton.grid(column=2, row=0, rowspan=2, sticky="NS")

# Right Window. Contains all the buttons that the user has added
canvas = tk.LabelFrame(root, bd=0, highlightthickness=0, bg='light blue', text=" Buttons ")
canvas.pack(fill="y", side="left")
colors = ["black", "white", "red", "green", "blue"]


#Threading
global finish
finish = False

control_thread = Thread(target=run, daemon=True)
control_thread.start()

root.mainloop()
control_thread.join()