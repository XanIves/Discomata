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


########################################################################
# Here are the global variables that need to be shared across threads. #
#
########################################################################

# A boolean IntVar. 0 = False, 1 = True for deleting messages after a short delay upon sending.
global deleteMessage

# This variable will store the list of buttons next to user buttons to be deleted.
global DELETE_BUTTONS;  DELETE_BUTTONS = []

# This variable stores the list of commands that the user has created.
global MACRO_BUTTONS;    MACRO_BUTTONS = []

# This will serve as the queue for my_background_task to check and read from. When value is "NULL", loop skips posting message
global MESSAGE;         MESSAGE = "NULL"

global chatLog; chatLog = ""
global SERVER_ID;           SERVER_ID       = 495421572786683918
global SERVER_NAME;         SERVER_NAME     = "The Server"
global SERVER_LIST;         SERVER_LIST     = []

global CHANNEL_ID;          CHANNEL_ID      = 748651797350187139
global CHANNEL_NAME;        CHANNEL_NAME    = "test"
global CHANNEL_LIST;        CHANNEL_LIST    = []

global CONSOLE_TEXT;        CONSOLE_TEXT    = "Starting up program..."
global CHAT_TEXT;           CHAT_TEXT       = ""
global LAST_USERNAME;       LAST_USERNAME   = ""

saveFileName = "addedButtons.ini"
client = discord.Client()
load_dotenv()           #Load discord keys and codes from .env file

# Create class to handle discord.py bot information
class DiscordBot:
    def __init__(self, token):
        self.token = token
        self.client = discord.Client()

    def run(self):
        self.client.run(self.token)



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
    userProfilePicture = message.author.avatar_url

    if (username != LAST_USERNAME):
        updateConsole("\n"+username+":\n"+message.content, chatConsole)
        updateChatWindow("<h4>"+username+":</h4>"+message.content)
        #updateChatWindow("<img src='"userProfilePicture"' width='50' height='50'/>")
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
    for guild in client.guilds:
        print(guild.name)
    for guild in client.guilds:
        if guild.id == SERVER_ID:
            for channel in guild.channels:
                if channel.type == discord.ChannelType.text:
                    CHANNEL_LIST.append(channel.name)
                    print("Channel: " + channel.name, botConsole)
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
    global SERVER_LIST, CHANNEL_LIST, SERVER_ID
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
    global MACRO_BUTTONS, SAVE_BUTTON, DELETE_BUTTONS
    if name and command:
        addedButtonTuple = [(ttk.Button(useCommandsScrollbar, text=name, command = lambda: discord_command(command))), command]
        MACRO_BUTTONS.append(addedButtonTuple)
        DELETE_BUTTONS.append(ttk.Button(useCommandsScrollbar, text="Remove", style="danger.TButton",command = lambda: removeCommand(MACRO_BUTTONS.index(addedButtonTuple))))

        for index, button in enumerate(MACRO_BUTTONS):
            button[0].grid(column=1, row=index, sticky="WENS", padx=10, pady=2)

        for index, button in enumerate(DELETE_BUTTONS):
            button.grid(column=2, row=index, sticky="WENS", padx=10, pady=2)

def removeCommand(commandIndex):
    global MACRO_BUTTONS, DELETE_BUTTONS
    print("commandIndex: ", commandIndex)
    MACRO_BUTTONS[commandIndex][0].grid_forget()
    DELETE_BUTTONS[commandIndex].grid_forget()

    del MACRO_BUTTONS[commandIndex]
    del DELETE_BUTTONS[commandIndex]

def setMessageDeleteValue(boolValue):
    global deleteMessage
    deleteMessage = boolValue

def choose_channel(channelArgument):
    global CHANNEL_ID
    CHANNEL_ID = int(channelArgument)

def choose_server(serverArgument):
    global SERVER_ID
    SERVER_ID = serverArgument

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
    global MACRO_BUTTONS
    print("Saving commands to " + saveFileName)
    updateConsole("Saving commands to " + saveFileName, botConsole)
    try:
        with open(saveFileName, "w") as file:
            for button in MACRO_BUTTONS:
                file.write(button[0].config('text')[-1]+"@")
                file.write(button[1]+"\n")
    except ValueError:
        print("Could not save to file: did you delete the MACRO_BUTTONS.ini file?")

# ______________________________________
#| Creation of GUI windows and elements |
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

# Root Window. Contains the Left Window and the Right Window
root = tk.Tk()
root.protocol("WM_DELETE_WINDOW", quit)
root.title("Discomata")
root.configure()
deleteMessage = tk.IntVar()
discordStyle = Style(theme='discord', themes_file='discordTheme.json')

#  _____________________________________________________
# | Frame Creation | For defining the layout of the GUI |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
botInfoFrame     = ttk.Frame      (root, width=335, height=150,relief="raised")
addCommandsFrame = ttk.LabelFrame (root, height=200, width=400, text=" Add Command ")
settingsFrame    = ttk.LabelFrame (botInfoFrame, text=" Settings ")
useCommandsFrame = ttk.LabelFrame (root, text=" Buttons ")
consoleNotebook  = ttk.Notebook   (root, style="primary.TNotebook")
settingsWindow   = ttk.PanedWindow(settingsFrame, orient=tk.VERTICAL)
channelsFrame    = ttk.PanedWindow(root, orient=tk.VERTICAL, width=100, height=150)

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

def updateChatWindow(newText):
    global chatLog
    chatLog += newText + "<br>"
    updatedChatlog = convertTextToHtml(chatLog)
    htmlWindow.outputbox.set_html(updatedChatlog)

def convertTextToHtml(textInMarkdownFormat):
    md2html = Markdown()
    textInHtmlFormat = md2html.convert(textInMarkdownFormat)
    return textInHtmlFormat

htmlChatConsoleWindow = tk.Frame(notebookTab3, width=335, height=150)
htmlChatConsoleWindow.pack(fill="both", side="left", expand=True)
htmlWindow = tk.Frame(htmlChatConsoleWindow, width=335, height=150)
htmlWindow.pack(fill=BOTH, expand=1)
htmlWindow.myfont = font.Font(family="Helvetica", size=12)
htmlWindow.pack(fill=BOTH, expand=1)
htmlWindow.inputeditor = Text(htmlWindow, width="1" , height = "0.25", font=htmlWindow.myfont)
htmlWindow.inputeditor.pack(fill=X, expand=1, side=BOTTOM)
htmlWindow.outputbox = HTMLLabel(htmlWindow, width="1", background="darkgrey", html="<h1>Welcome</h1>")
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
savedCommands = get_commands(saveFileName)
for commandTuple in savedCommands:
    add_user_command(commandTuple[0], commandTuple[1])

# Save Button
SAVE_BUTTON = ttk.Button(useCommandsFrame, text="Save Buttons", style="success.TButton", command = lambda: save_commands(saveFileName))
SAVE_BUTTON.grid(column=1, row=1, sticky="WENS", padx=10, pady=20, columnspan=2)

#  _________________________________________________
# | Bot Info | Information and settings for the bot |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
# fetch the username of the bot in the server it's connected to.

botUsernameLabel = ttk.Label(botInfoFrame, text="Loading . . .", style="primary.TLabel")
botUsernameLabel.pack(side=tk.LEFT, padx=10, pady=10)

#  __________________________________________________________________________________________________
# | "Settings" | Contains an entry field and a button to choose which server and channel to post to. |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾

# Entry field for changing server by ID
serverNameEntry = ttk.Entry(settingsFrame)
serverNameEntry.grid(column=1,row=2)
serverNameTitle = ttk.Label(settingsFrame, text="Server Id")
serverNameTitle.grid(column=0,row=2, sticky="W")
chooseServerButton = ttk.Button(
    settingsFrame,
    text="Save",
    style="success.TButton",
    command = lambda: choose_server(serverNameEntry.get())
)
chooseServerButton.grid(column=2, row=2, sticky="NW", padx=10, pady=5)


# Entry field for changing channel by ID
channelNameEntry = ttk.Entry(settingsFrame)
channelNameEntry.grid(column=1,row=3)
channelNameTitle = ttk.Label(settingsFrame, text="Channel Id")
channelNameTitle.grid(column=0,row=3, sticky="W")
chooseChannelButton = ttk.Button(
    settingsFrame,
    text="Save",
    style="success.TButton",
    command = lambda: choose_channel(channelNameEntry.get())
)
chooseChannelButton.grid(column=2, row=3, sticky="NW", padx=10, pady=5)

removeMessageTextLabel = ttk.Label(
    settingsFrame,
    text = "Delete Message\nAfter Post?",
    style="light.TLabel"
)
removeMessageTextLabel.grid(column=0, row=4, sticky="W")

removeMessageCheckBox = ttk.Checkbutton(
    settingsFrame,
    variable=deleteMessage,
    command = lambda: checkboxFunction()
)
removeMessageCheckBox.grid(column=1, row=4, sticky="NS", padx=10, pady=5, columnspan=2)

#  ________________________________________________________________________________
# | Packing | Defines the layout of the UI after all the buttons have been created |
#  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
channelsFrame.pack         (padx=5, pady=5,fill=Y,    side=LEFT, expand=NO)
addCommandsFrame.pack      (padx=5, pady=5,fill=BOTH, side=TOP)
settingsFrame.pack         (padx=5, pady=5,fill=BOTH, side=TOP)
useCommandsFrame.pack      (padx=5, pady=5,fill=BOTH, side=TOP,expand=YES)
botInfoFrame.pack          (padx=5, pady=5,fill=BOTH, side=BOTTOM)


#Threading written by Benedict Wilkins AI, taken from his example blog post
global FINISH
FINISH = False

control_thread = Thread(target=run, daemon=True)
control_thread.start()

root.mainloop()
control_thread.join(1)
