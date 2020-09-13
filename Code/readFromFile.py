
def getCommands(saveFileName):
    print("Opening saved commands from " + saveFileName)
    file = open(saveFileName, "r")
    commandList = []
    if file.mode == 'r':
        lines =file.readlines()
        for line in lines:
            parts = line.split('@', 1)
            commandTuple = [parts[0], parts[1]]
            commandList.append(commandTuple)
        return commandList
    else:
        print("Error: {saveFileName} could not be opened")
        return