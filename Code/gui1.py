#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 19:25:31 2020

Python Bot with GUI for Discord macro creation and execution

@author: Alexander G. Ives

Initially based on a multi-threaded tkinter example template by Benedict Wilkins AI
"""

import asyncio, discord, os, time
import readFromFile
import tkinter as tk
from tkinter import ttk
from threading import Thread

from dotenv import load_dotenv
load_dotenv()           #Load discord keys and codes from .env file

# My variables
global message          # This will serve as the queue for my_background_task to check and read from. When value is "empty", loop skips posting message
message = "NULL"

global userButtons      # Create a list to store user-inputted button templates
userButtons = []

global deleteUserButtons # Create a list of buttons to aside userButtons buttons so that each individual button can be deleted.
deleteUserButtons = []

global channelID        # Current channel for the bot to post in
channelID = 748651797350187139  # This is just my default testing channel in discord. Defaults to this channel if the user doesn't input anything

global deleteMessage    # Controls whether a message gets deleted after very short period of time (~1s). Useful for calling Diceparser, less for Avrae
#look for the declaration of this variable after the root declaration

client = discord.Client()
saveFileName = "addedButtons.ini"
global saveButton   # Green "Save" button to save current button states for later


# Discord syncing stuff
async def my_background_task():
    global message, channelID, finish, deleteMessage
    await client.wait_until_ready() # ensures cache is loaded
    channel = client.get_channel(id=channelID) # replace with target channel id

    while not client.is_closed():
        if message != "NULL":
            channel = client.get_channel(id=channelID) # replace with target channel id
            sentMessage = await channel.send(message)
            if deleteMessage.get() == 1:
                await sentMessage.delete()  # deletes the original command posted to keep the chat clean
            message = "NULL"
        await asyncio.sleep(0.2)  # Measured in seconds. Set to 300 for 5 minutes

@client.event
async def on_ready():   #Partially written by Benedict Wilkins AI
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #await channel.send("!beyond https://ddb.ac/characters/28780677/kdQS4u")
    client.loop.create_task(my_background_task()) # best to put it in here


class Sleep:    # This class was written by Benedict Wilkins AI
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
    global userButtons, saveButton, deleteUserButtons
    if name and command:
        addedButtonTuple = [(tk.Button(canvas, text=name, command = lambda: avrae_command(command))), command]
        userButtons.append(addedButtonTuple)
        deleteUserButtons.append(tk.Button(canvas, text="Remove",bg="red", command = lambda: removeCommand(userButtons.index(addedButtonTuple))))

        for index, button in enumerate(userButtons):
            button[0].grid(column=1, row=index, sticky="WENS", padx=10, pady=2)

        for index, button in enumerate(deleteUserButtons):
            button.grid(column=2, row=index, sticky="WENS", padx=10, pady=2)

        saveButton.grid(column=1, row=len(userButtons), sticky="WENS", padx=10, pady=20)

def removeCommand(commandIndex):
    global userButtons, deleteUserButtons
    print("commandIndex: ", commandIndex)
    userButtons[commandIndex][0].grid_forget()
    deleteUserButtons[commandIndex].grid_forget()

    del userButtons[commandIndex]
    del deleteUserButtons[commandIndex]
    print(userButtons)

def setMessageDeleteValue(boolValue):
    global deleteMessage
    deleteMessage = boolValue

def choose_channel(channelArgument):
    global channelID
    channelID = int(channelArgument)

def save_buttons(saveFileName):
    print("save the buttons")
    global userButtons
    readFromFile.save_commands(saveFileName, userButtons)

def checkboxFunction():
    global deleteMessage
    print("deleteMessage", deleteMessage.get())

def quit():
    global finish
    finish = True
    root.destroy()


# ______________________________________
#| Creation of GUI windows and elements |
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

# Root Window. Contains the Left Window and the Right Window
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit)
root.title("D&D Macro Bot")
root.minsize(200,50)
root.configure(background='light blue')
deleteMessage = tk.IntVar()

# Left Top Window. Contains buttons for adding commands
subWindow = tk.LabelFrame(root,bd=1,bg='light blue', height=200, text=" Add New Command ", relief="ridge")
subWindow.pack(fill="y", side="left")

buttonNameEntry = tk.Entry(subWindow)       # Entry field for adding a new command's name
buttonNameEntry.grid(column=1,row=0, sticky="WESN")
buttonNameTitle = tk.Label(subWindow, text="Command Name",bg='light blue')
buttonNameTitle.grid(column=0,row=0, sticky="WS")

buttonCommandEntry = tk.Entry(subWindow)    # Entry field for adding a new command's text to be executed
buttonCommandEntry.grid(column=1,row=1, sticky="WESN")
buttonCommandTitle = tk.Label(subWindow, text="Command Text",bg='light blue')
buttonCommandTitle.grid(column=0,row=1, sticky="WS")

addButtonButton = tk.Button(subWindow, text="Add", command = lambda: add_user_command(buttonNameEntry.get(), buttonCommandEntry.get()))
addButtonButton.grid(column=2, row=0, rowspan=2, sticky="NS")

# Bottom of Left Top Window. Contains an entry field and a button to choose which channel to post to.
channelWindow = tk.LabelFrame(subWindow,bd=1,bg='light blue', height=200, text=" Channel Settings ", relief="ridge")
channelWindow.grid(column=0,row=2, sticky="WS", columnspan=3, pady=20)

channelNameEntry = tk.Entry(channelWindow)       # Entry field for adding a new command's name
channelNameEntry.grid(column=1,row=2)
channelNameTitle = tk.Label(channelWindow, text="Channel Id           ",bg='light blue')
channelNameTitle.grid(column=0,row=2, sticky="WS")

chooseChannelButton = tk.Button(channelWindow, text="Set Channel", command = lambda: choose_channel(channelNameEntry.get()))
chooseChannelButton.grid(column=2, row=2, sticky="NW", padx=10, pady=5)

removeMessageCheckBox = tk.Checkbutton(channelWindow, text="Delete Message\nAfter Post", variable=deleteMessage, command = lambda: checkboxFunction())
removeMessageCheckBox.grid(column=2, row=3, sticky="NS", padx=10, pady=5)

# Right Window. Contains all the buttons that the user has added
canvas = tk.LabelFrame(root, bd=0, highlightthickness=0, bg='light blue', text=" Buttons ")
canvas.pack(fill="y", side="left")
colors = ["black", "white", "red", "green", "blue"]
    # Save Button
saveButton = tk.Button(canvas, text="Save Buttons", command = lambda: save_buttons(saveFileName), bg='green', fg="white")
saveButton.grid(column=1, row=0, sticky="WENS", padx=10, pady=20)

# Open save file for previous commands, and restore saved buttons
savedCommands = readFromFile.get_commands(saveFileName)
print(savedCommands)

for commandTuple in savedCommands:
    add_user_command(commandTuple[0], commandTuple[1])

#Threading written by Benedict Wilkins AI, taken from his example blog post
global finish
finish = False

control_thread = Thread(target=run, daemon=True)
control_thread.start()

root.mainloop()
control_thread.join(1)