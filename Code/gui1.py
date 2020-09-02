#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 10:27:51 2019

Example use of tkinter with python threading.

@author: Benedict Wilkins AI & Alexander G Ives
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
    channel = client.get_channel(id=748651797350187139) # replace with target channel id
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
    # This function will take in command and enter the text of it into discord.
    # Won't work if you want to type "empty"
    global message
    if command!=None and command!="empty":
        print("Button was pressed: " + command)
        message = command
    else:
        print("Error: empty command issued.")

def add_user_command(name, command):
    global userButtons
    userButtons.append(tk.Button(canvas, text=name, command = lambda: avrae_command(command)))
    print(userButtons)
    for index, button in enumerate(userButtons):
        print("index = " + str(index))
        button.grid(column=1, row=index, sticky="WENS", padx=10, pady=2)

def quit():
    global finish
    finish = True
    root.destroy()


#Threading
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit)
root.title("Python Tkinter Text Box")
root.minsize(600,400)
root.configure(background='light blue')


#GUI
# Canvas
canvas = tk.Canvas(root, bd=0, highlightthickness=0, bg='light blue')
canvas.grid(column=1, row = 0)
colors = ["black", "white", "red", "green", "blue"]


# Button inputs to allow user to add additional commands
subWindow = tk.Frame(root, bg='light blue', height=200)
subWindow.grid(column= 0, row = 0, sticky="WENS")
buttonNameEntry = tk.Entry(subWindow)
buttonNameEntry.grid(column=0,row=0)

buttonCommandEntry = tk.Entry(subWindow)
buttonCommandEntry.grid(column=1,row=0)

addButtonButton = tk.Button(subWindow, text="Add", command = lambda: add_user_command(buttonNameEntry.get(), buttonCommandEntry.get()))
addButtonButton.grid(column=2, row = 0)


#Threading
global finish
finish = False

control_thread = Thread(target=run, daemon=True)
control_thread.start()

root.mainloop()
control_thread.join()