def get_commands(saveFileName):
    print("Opening saved commands from " + saveFileName)
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
        try:
            file.close()
        except:
            print("Error: {saveFileName} could not be opened")
        return

def save_commands(saveFileName, userButtons):
    print("Saving commands to " + saveFileName)
    try:
        file = open(saveFileName, "w")
        for button in userButtons:
            file.write(button[0].config('text')[-1]+"@")
            file.write(button[1]+"\n")
        file.close
    except ValueError:
        print("Could not save to file: did you delete the userButtons.ini file?")

