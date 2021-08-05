#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 19:25:31 2020

Python Bot with GUI for Discord macro creation and execution

@author: Alexander G. Ives

Initially based on a multi-threaded tkinter example template by Benedict Wilkins AI
"""

import asyncio, discord, os, time
from tkinter.constants import LEFT
import tkinter as tk
from tkinter import ttk
from threading import Thread
import ttkbootstrap
from ttkbootstrap import Style

from dotenv import load_dotenv
load_dotenv()           #Load discord keys and codes from .env file

# My variables
global message          # This will serve as the queue for my_background_task to check and read from. When value is "NULL", loop skips posting message
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

global consoleText
consoleText = "Starting up program"

global chatText
chatText = ""

global lastUsername
lastUsername = ""

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
async def on_message(message):
    global lastUsername
    username = message.author.name
    if (username != lastUsername):
        updateChat(username+"\n"+message.content)
        lastUsername = username
    else:
        updateChat(message.content)


@client.event
async def on_ready():   #Partially written by Benedict Wilkins AI
    updateConsole(consoleText)
    print('Logged in as')
    updateConsole("Logged in as ")
    updateConsole(client.user.name)
    updateConsole(client.user.id)
    updateConsole('------')
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
    updateConsole("Discord Token: " + token)
    client.run(token)

def avrae_command(command):
    # This function will take in command and enter it into discord as a text post.
    global message
    if command!=None and command!="empty":
        updateConsole("Message sent: " + command)
        message = command
    else:
        print("Error: empty command issued.")

def add_user_command(name, command):
    global userButtons, saveButton, deleteUserButtons
    if name and command:
        addedButtonTuple = [(ttk.Button(canvas, text=name, command = lambda: avrae_command(command))), command]
        userButtons.append(addedButtonTuple)
        deleteUserButtons.append(ttk.Button(canvas, text="Remove", style="danger.TButton",command = lambda: removeCommand(userButtons.index(addedButtonTuple))))

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
    save_commands(saveFileName, userButtons)

def checkboxFunction():
    global deleteMessage
    print("deleteMessage", deleteMessage.get())

def quit():
    global finish
    finish = True
    root.destroy()

def updateConsole(inputText):
    print(inputText)
    botConsole.configure(state="normal")
    botConsole.insert(tk.END, "\n"+str(inputText))
    botConsole.configure(state="disabled")

# This function updates the text in the chat console
def updateChat(inputText):
    chatConsole.configure(state="normal")
    chatConsole.insert(tk.END, "\n"+str(inputText))
    chatConsole.configure(state="disabled")

def get_commands(saveFileName):
    print("Opening saved commands from " + saveFileName)
    updateConsole("Opening saved commands from " + saveFileName)
    commandList = []
    file = open(saveFileName, "r")
    if file.mode == 'r':
        lines =file.readlines()
        for line in lines:
            parts = line.split('@', 1)
            commandTuple = [parts[0], parts[1].rstrip('\n')]
            commandList.append(commandTuple)
        file.close()
        return commandList
    else:
        print("Error: {saveFileName} could not be opened")
        updateConsole("Error: {saveFileName} could not be opened")
        try:
            file.close()
        except:
            print("Error: {saveFileName} could not be opened")
        return

def save_commands(saveFileName, userButtons):
    print("Saving commands to " + saveFileName)
    updateConsole("Saving commands to " + saveFileName)
    try:
        file = open(saveFileName, "w")
        for button in userButtons:
            file.write(button[0].config('text')[-1]+"@")
            file.write(button[1]+"\n")
        file.close
    except ValueError:
        print("Could not save to file: did you delete the userButtons.ini file?")

# ______________________________________
#| Creation of GUI windows and elements |
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Root Window. Contains the Left Window and the Right Window
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit)
root.title("D&D Macro Bot")
root.minsize(600,460)
root.configure()
# style = Style(theme="darkly")
deleteMessage = tk.IntVar()
style = Style(theme='discord', themes_file='discordTheme.json')


# style = ttk.Style(root)
# root.tk.call ('source', '..\\Azure-ttk-theme-main\\azure-dark.tcl')
# style.theme_use ('azure-dark')

#  __________________________________________________________
# | "Add New Command" | Contains buttons for adding commands |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
subWindow = ttk.LabelFrame(root, height=200, text=" Add Command ")

buttonNameEntry = ttk.Entry(subWindow)       # Entry field for adding a new command's name
buttonNameEntry.grid(column=1,row=0, sticky="WESN")
buttonNameTitle = ttk.Label(subWindow, text="Command Name")
buttonNameTitle.grid(column=0,row=0, sticky="W",padx=10, pady=5)

buttonCommandEntry = ttk.Entry(subWindow)    # Entry field for adding a new command's text to be executed
buttonCommandEntry.grid(column=1,row=1, sticky="WESN", pady=10,)
buttonCommandTitle = ttk.Label(subWindow, text="Command Text")
buttonCommandTitle.grid(column=0,row=1, sticky="W",padx=10, pady=5)

addButtonButton = ttk.Button(subWindow,style="primary.TButton",text="Add", command = lambda: add_user_command(buttonNameEntry.get(), buttonCommandEntry.get()))
addButtonButton.grid(column=2, row=0, rowspan=2, sticky="NS" ,padx=10, pady=10)

#  _______________________________________________________________________________________________
# | "Channel Settings" | Contains an entry field and a button to choose which channel to post to. |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
channelWindow = ttk.LabelFrame(root, height=200, text=" Settings ")

channelNameEntry = ttk.Entry(channelWindow)       # Entry field for adding a new command's name
channelNameEntry.grid(column=1,row=2)
channelNameTitle = ttk.Label(channelWindow, text="Channel Id           ")
channelNameTitle.grid(column=0,row=2, sticky="W")

chooseChannelButton = ttk.Button(channelWindow, text="Set Channel", command = lambda: choose_channel(channelNameEntry.get()))
chooseChannelButton.grid(column=2, row=2, sticky="NW", padx=10, pady=5)

removeMessageCheckBox = ttk.Checkbutton(channelWindow, text="Delete Message\nAfter Post", variable=deleteMessage, command = lambda: checkboxFunction())
removeMessageCheckBox.grid(column=2, row=3, sticky="NS", padx=10, pady=5)

#  _________________________________________________________________________
# | "Console" | A text console for the user to input messages into directly |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Notebook
notebook = ttk.Notebook(root,style="primary.TNotebook")
# Tab 1
notebookTab1 = ttk.Frame(notebook, width=335, height=150, style="primary.TNotebook")
notebookTab2 = ttk.Frame(notebook, width=335, height=150)
notebook.add(notebookTab1, text='Bot Console')
notebook.add(notebookTab2, text='Chat Console')

notebook.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
# Bot Console
botConsole = tk.Text(notebookTab1,bg="#36393F", fg="#ffffff")
botConsole.pack(fill="both", side="left", expand=True)
# Chat Console
chatConsoleWindow = tk.PanedWindow(notebookTab2, orient=tk.VERTICAL)
chatConsoleWindow.pack(fill="both", side="left", expand=True)
chatConsole = tk.Text(chatConsoleWindow,bg="#36393F", fg="#ffffff")
chatConsole.pack(fill="both", side="left", expand=True)

#  ______________________________________________________________
# | "Buttons" | Contains all the buttons that the user has added |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
canvas = ttk.LabelFrame(root, text=" Buttons ", width = 500)

colors = ["black", "white", "red", "green", "blue"]
    # Save Button
saveButton = ttk.Button(canvas, text="Save Buttons", style="success.TButton", command = lambda: save_buttons(saveFileName))
saveButton.grid(column=1, row=0, sticky="WENS", padx=10, pady=20, columnspan=2)

# Open save file for previous commands, and restore saved buttons
savedCommands = get_commands(saveFileName)
print(savedCommands)

for commandTuple in savedCommands:
    add_user_command(commandTuple[0], commandTuple[1])

#  ________________________________________________________________________________
# | Packing | Defines the layout of the UI after all the buttons have been created |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
subWindow.pack(fill="both",side="top",padx=5, pady=10,)
channelWindow.pack(fill="both", side="top",padx=5, pady=10,)
#channelWindow.grid(column=0,row=2, sticky="WS", columnspan=3, pady=20)
canvas.pack(fill="y", side="left", expand=tk.YES,padx=5, pady=10,)





#Threading written by Benedict Wilkins AI, taken from his example blog post
global finish
finish = False

control_thread = Thread(target=run, daemon=True)
control_thread.start()

root.mainloop()
control_thread.join(1)