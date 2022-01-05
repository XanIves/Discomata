#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 19:25:31 2020

Python Bot with GUI for Discord macro creation and execution

@author: Alexander G. Ives

Initially based on a multi-threaded tkinter example template by Benedict Wilkins AI
"""
import asyncio
import os
import time
import tkinter as tk
from threading import Thread
from tkinter import *
from tkinter import constants, filedialog, font, ttk

import discord
from dotenv import load_dotenv
from markdown2 import Markdown
from pygments.formatters import html
from tkhtmlview import HTMLLabel

import ttkbootstrap
from ttkbootstrap import Style

load_dotenv()           #Load discord keys and codes from .env file

# This will serve as the queue for my_background_task to check and read from. When value is "NULL", loop skips posting message
global MESSAGE
MESSAGE = "NULL"

# This variable stores the list of commands
global USER_BUTTONS
USER_BUTTONS = []

# This variable will store the list of buttons next to user buttons to be deleted.
global DELETE_USER_BUTTONS
DELETE_USER_BUTTONS = []

global CHANNEL_ID
CHANNEL_ID = 748651797350187139

global deleteMessage    # Controls whether a message gets deleted after very short period of time (~1s). Useful for calling Diceparser, less for Avrae
#look for the declaration of this variable after the root declaration

client = discord.Client()
SAVE_FILE_NAME = "addedButtons.ini"
global SAVE_BUTTON   # Green "Save" button to save current button states for later

global CONSOLE_TEXT
CONSOLE_TEXT = "Starting up program"

global CHAT_TEXT
CHAT_TEXT = ""

global LAST_USERNAME
LAST_USERNAME = ""

# Discord syncing stuff
async def my_background_task():
    global MESSAGE, CHANNEL_ID, FINISH, deleteMessage
    await client.wait_until_ready() # ensures cache is loaded
    channel = client.get_channel(id=CHANNEL_ID) # replace with target channel id

    while not client.is_closed():
        if MESSAGE != "NULL":
            channel = client.get_channel(id=CHANNEL_ID) # replace with target channel id
            sentMessage = await channel.send(MESSAGE)
            if deleteMessage.get() == 1:
                await sentMessage.delete()  # deletes the original command posted to keep the chat clean
            MESSAGE = "NULL"
        await asyncio.sleep(0.2)  # Measured in seconds. Set to 300 for 5 minutes

@client.event
async def on_message(message):
    global LAST_USERNAME
    username = message.author.name
    if (username != LAST_USERNAME):
        updateConsole("\n"+username+":\n"+message.content, chatConsole)
        updateChatWindow("\n***"+username+":***\n"+message.content)
        LAST_USERNAME = username
    else:
        updateConsole(message.content, chatConsole)
        updateChatWindow(message.content)


@client.event
async def on_ready():   #Partially written by Benedict Wilkins AI
    updateConsole(CONSOLE_TEXT, botConsole)
    print('Logged in as')
    updateConsole("Logged in as ", botConsole)
    updateConsole(client.user.name, botConsole)
    updateConsole(client.user.id, botConsole)
    updateConsole('------', botConsole)
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
        self.FINISH = self.start + self.wait

    def __exit__(self, type, value, traceback):
        while self.__t() < self.FINISH:
            time.sleep(1./1000.)

    def __t(self):
        return int(round(time.time() * 1000))


def after(t, fun, *args):
    global FINISH
    if not FINISH:
        root.after(t, fun, *args)

def run():
    token = os.environ.get("DISCORD_TOKEN")
    updateConsole("Discord Token: " + token, botConsole)
    client.run(token)

def quit():
    global FINISH
    FINISH = True
    root.destroy()

def discord_command(command):
    # This function will take in command and enter it into discord as a text post.
    global MESSAGE
    if command!=None and command!="empty":
        updateConsole("Message sent: " + command, botConsole)
        MESSAGE = command
    else:
        print("Error: empty command issued.")

def add_user_command(name, command):
    global USER_BUTTONS, SAVE_BUTTON, DELETE_USER_BUTTONS
    if name and command:
        addedButtonTuple = [(ttk.Button(useCommandsScrollbar, text=name, command = lambda: discord_command(command))), command]
        USER_BUTTONS.append(addedButtonTuple)
        DELETE_USER_BUTTONS.append(ttk.Button(useCommandsScrollbar, text="Remove", style="danger.TButton",command = lambda: removeCommand(USER_BUTTONS.index(addedButtonTuple))))

        for index, button in enumerate(USER_BUTTONS):
            button[0].grid(column=1, row=index, sticky="WENS", padx=10, pady=2)

        for index, button in enumerate(DELETE_USER_BUTTONS):
            button.grid(column=2, row=index, sticky="WENS", padx=10, pady=2)

def removeCommand(commandIndex):
    global USER_BUTTONS, DELETE_USER_BUTTONS
    print("commandIndex: ", commandIndex)
    USER_BUTTONS[commandIndex][0].grid_forget()
    DELETE_USER_BUTTONS[commandIndex].grid_forget()

    del USER_BUTTONS[commandIndex]
    del DELETE_USER_BUTTONS[commandIndex]

def setMessageDeleteValue(boolValue):
    global deleteMessage
    deleteMessage = boolValue

def choose_channel(channelArgument):
    global CHANNEL_ID
    CHANNEL_ID = int(channelArgument)

def checkboxFunction():
    global deleteMessage
    print("deleteMessage", deleteMessage.get())

def updateConsole(inputText, targetConsole):
    print(inputText)
    targetConsole.configure(state="normal")
    targetConsole.insert(tk.END, "\n"+str(inputText))
    targetConsole.configure(state="disabled")

def get_commands(saveFileName):
    print("Opening saved commands from " + saveFileName)
    updateConsole("Opening saved commands from " + saveFileName, botConsole)
    commandList = []
    with open(saveFileName, "r") as file:
        if file.mode == 'r':
            lines =file.readlines()
            for line in lines:
                parts = line.split('@', 1)
                commandTuple = [parts[0], parts[1].rstrip('\n')]
                commandList.append(commandTuple)
        else:
            print("Error: {saveFileName} could not be opened")
            updateConsole("Error: {saveFileName} could not be opened", botConsole)
    return commandList

def save_commands(saveFileName):
    global USER_BUTTONS
    print("Saving commands to " + saveFileName)
    updateConsole("Saving commands to " + saveFileName, botConsole)
    try:
        with open(saveFileName, "w") as file:
            for button in USER_BUTTONS:
                file.write(button[0].config('text')[-1]+"@")
                file.write(button[1]+"\n")
    except ValueError:
        print("Could not save to file: did you delete the USER_BUTTONS.ini file?")

# ______________________________________
#| Creation of GUI windows and elements |
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

# Root Window. Contains the Left Window and the Right Window
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit)
root.title("Discomata")
root.minsize(600,460)
root.configure()
deleteMessage = tk.IntVar()
style = Style(theme='discord', themes_file='discordTheme.json')

#  _____________________________________________________
# | Frame Creation | For defining the layout of the GUI |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
addCommandsFrame = ttk.LabelFrame(root, height=200, width=400, text=" Add Command ")
settingsFrame    = ttk.LabelFrame(root, text=" Settings ")
useCommandsFrame = ttk.LabelFrame(root, text=" Buttons ")
consoleNotebook  = ttk.Notebook  (root, style="primary.TNotebook")

#  _______________________________________________________
# | "Add Commands" | Contains buttons for adding commands |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
buttonNameEntry = ttk.Entry(addCommandsFrame)       # Entry field for adding a new command's name
buttonNameEntry.grid(column=1,row=0)
buttonNameTitle = ttk.Label(addCommandsFrame, text="Command Name")
buttonNameTitle.grid(column=0,row=0)

buttonCommandEntry = ttk.Entry(addCommandsFrame)    # Entry field for adding a new command's text to be executed
buttonCommandEntry.grid(column=1,row=1)
buttonCommandTitle = ttk.Label(addCommandsFrame, text="Command Text")
buttonCommandTitle.grid(column=0,row=1)

addButtonButton = ttk.Button(addCommandsFrame,width = 4,style="primary.TButton",text="Add", command = lambda: add_user_command(buttonNameEntry.get(), buttonCommandEntry.get()))
addButtonButton.grid(column=2, row=0, rowspan=2, sticky="NS", padx=10)

#  _______________________________________________________________________________________________
# | "Settings" | Contains an entry field and a button to choose which channel to post to. |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
channelNameEntry = ttk.Entry(settingsFrame)       # Entry field for adding a new command's name
channelNameEntry.grid(column=1,row=2)
channelNameTitle = ttk.Label(settingsFrame, text="Channel Id")
channelNameTitle.grid(column=0,row=2, sticky="W")

chooseChannelButton = ttk.Button(
    settingsFrame,
    text="Save",
    style="success.TButton",
    command = lambda: choose_channel(channelNameEntry.get())
)
chooseChannelButton.grid(column=2, row=2, sticky="NW", padx=10, pady=5)

removeMessageTextLabel = ttk.Label(
    settingsFrame,
    text = "Delete Message\nAfter Post?",
    style="light.TLabel"
)
removeMessageTextLabel.grid(column=0, row=3, sticky="W")

removeMessageCheckBox = ttk.Checkbutton(
    settingsFrame,
    variable=deleteMessage,
    command = lambda: checkboxFunction()
)
removeMessageCheckBox.grid(column=1, row=3, sticky="NS", padx=10, pady=5, columnspan=2)

#  _________________________________________________________________________
# | "Console" | A text console for the user to input messages into directly |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# Tab 1
notebookTab1 = ttk.Frame(consoleNotebook, width=335, height=150, style="primary.TNotebook")
notebookTab2 = ttk.Frame(consoleNotebook, width=335, height=150)
notebookTab3 = ttk.Frame(consoleNotebook, width=335, height=150)
consoleNotebook.add(notebookTab1, text='Bot Console')
consoleNotebook.add(notebookTab2, text='Chat Console')
consoleNotebook.add(notebookTab3, text='HTML Chat Console')

consoleNotebook.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
# Bot Console
botConsole = tk.Text(notebookTab1,bg="#36393F", fg="#ffffff")
botConsole.pack(fill="both", side="left", expand=True)
# Chat Console
chatConsoleWindow = tk.PanedWindow(notebookTab2, orient=tk.VERTICAL)
chatConsoleWindow.pack(fill="both", side="left", expand=True)
chatConsole = tk.Text(chatConsoleWindow,bg="#36393F", fg="#ffffff")
chatConsole.pack(fill="both", side="left", expand=True)
chatConsole.configure(state="disabled")
# HTML Chat Console
def onInputChange(event):
    newText = htmlWindow.inputeditor.get(1.0, tk.END)
    discord_command(newText)
    htmlWindow.inputeditor.delete(1.0, tk.END)

def updateChatWindow(text):
    newText = text
    oldHtmlText = convertTextToHtml(htmlWindow.outputbox.get(1.0, tk.END))
    newHtmlText = convertTextToHtml(newText)
    htmlWindow.outputbox.set_html(oldHtmlText+newHtmlText)

def convertTextToHtml(markdownText):
    md2html = Markdown()
    html = md2html.convert(markdownText)
    return html

htmlChatConsoleWindow = tk.Frame(notebookTab3, width=335, height=150)
htmlChatConsoleWindow.pack(fill="both", side="left", expand=True)
htmlWindow = tk.Frame(htmlChatConsoleWindow, width=335, height=150)
htmlWindow.pack(fill=BOTH, expand=1)
htmlWindow.myfont = font.Font(family="Helvetica", size=14)
htmlWindow.pack(fill=BOTH, expand=1)
htmlWindow.inputeditor = Text(htmlWindow, width="1" , height = "0.25", font=htmlWindow.myfont)
htmlWindow.inputeditor.pack(fill=X, expand=1, side=BOTTOM)
htmlWindow.outputbox = HTMLLabel(htmlWindow, width="1", background="gray", html="<h1>Welcome</h1>")
htmlWindow.outputbox.pack(fill="both", expand=1, side=TOP)
htmlWindow.outputbox.fit_height()
htmlWindow.inputeditor.bind("<Return>", onInputChange)

#  ______________________________________________________________
# | "Buttons" | Contains all the buttons that the user has added |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#Scrollbar
useCommandsScrollbar = ttk.Scrollbar (useCommandsFrame, orient="vertical")
useCommandsScrollbar.grid(column=1, row=0)

#Command Buttons
savedCommands = get_commands(SAVE_FILE_NAME)
for commandTuple in savedCommands:
    add_user_command(commandTuple[0], commandTuple[1])

# Save Button
SAVE_BUTTON = ttk.Button(useCommandsFrame, text="Save Buttons", style="success.TButton", command = lambda: save_commands(SAVE_FILE_NAME))
SAVE_BUTTON.grid(column=1, row=1, sticky="WENS", padx=10, pady=20, columnspan=2)

#  _________________________________________________
# | Bot Info | Information and settings for the bot |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

#  ________________________________________________________________________________
# | Packing | Defines the layout of the UI after all the buttons have been created |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
addCommandsFrame.pack      (fill=tk.BOTH, side=tk.TOP,padx=5, pady=10)
settingsFrame.pack         (fill=tk.BOTH, side=tk.TOP,padx=5, pady=10)
useCommandsFrame.pack      (fill=tk.BOTH, side=tk.TOP,padx=5, pady=10,expand=tk.YES)



#Threading written by Benedict Wilkins AI, taken from his example blog post
global FINISH
FINISH = False

control_thread = Thread(target=run, daemon=True)
control_thread.start()

root.mainloop()
control_thread.join(1)
