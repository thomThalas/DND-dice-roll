import customtkinter as ctk
import json
import random
from enum import Enum
import os
from dotenv import load_dotenv
from copy import deepcopy
import re

load_dotenv()

root = ctk.CTk()
#root.resizable(False, False)
root.geometry("800x800")

CONFIG_PATH = os.getenv("CONFIG_PATH")

ALL_LETTERS = [
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z","space"
]


NUMBERS = ["1","2","3","4","5","6","7","8","9","0"]

RANDOM_TEXT = ["#", "/", "*", "^", "Å", "Æ", "Ø", "?"]

config = {}

with open(CONFIG_PATH, "r") as f:
    config = json.loads(f.read())

def CreateDefaultValue(parent: any, key: str, defaultValue: any):
    parent[key] = parent[key] if key in parent else defaultValue

def CreateDefaultDiceConfig(diceConfig):
    print(diceConfig)
    for i in range(max([len(diceConfig["dice"]), len(diceConfig["bonus"]), len(diceConfig["advantage"])])):
        if i >= len(diceConfig["dice"]): diceConfig["dice"].append(diceConfig["dice"][-1])
        if i >= len(diceConfig["bonus"]): diceConfig["bonus"].append(diceConfig["bonus"][-1])
        if i >= len(diceConfig["advantage"]): diceConfig["advantage"].append(diceConfig["advantage"][-1])
    print(diceConfig)

            

def GetDiceFromDiceConfig(diceConfigValue: list[int]):
    diceGroup: list[list[int]] = []
    for i, value in enumerate(diceConfigValue):
        nestedI = i % 2
        if nestedI == 0: diceGroup.append([])
        diceGroup[-1].append(diceConfigValue[i])
    return diceGroup


#region SET VALUES TO THEIR DEFAULT IF NOT SET IN CONFIG
for name in config["settings"]["binds"]:
    for c in config[name]:
        CreateDefaultValue(c, "advantage", [0])
        CreateDefaultValue(c, "bonus", [0])
        CreateDefaultValue(c, "dice", [[1,20]])
        CreateDefaultDiceConfig(c)
CreateDefaultValue(config["settings"], "animation", "RANDOM_NUMBERS")
CreateDefaultValue(config["settings"], "animationSpeed", 1.25)
CreateDefaultValue(config["settings"], "searchType", "FLEXIBLE")
CreateDefaultValue(config["settings"],"gui",{})
CreateDefaultValue(config["settings"]["gui"], "currentDiceSizeMul", 1.0)
CreateDefaultValue(config["settings"]["gui"], "diceResultSizeMul", 1.0)
CreateDefaultValue(config["settings"]["gui"], "searchSizeMul", 1.0)
CreateDefaultValue(config["settings"]["gui"], "tabsSizeMul", 1.0)
settings = config["settings"]
#endregion
print(config)


allKeyBinds: list = []
def KeyPressed(event):
    for f in allKeyBinds:
        f(event)
root.bind("<Key>", KeyPressed)


def DirectionParse(startIndex, parsingText, endLetters, parseLeft = False, defaultValue: any = "0"):
    result = ""
    if startIndex == -1:
        return defaultValue
    i = startIndex + (-1 if parseLeft else 1)
    if i >= 0:
        while i < len(parsingText) and i > -1 and parsingText[i] not in endLetters:
            if parseLeft:
                result = parsingText[i] + result
            else:
                result += parsingText[i]   
            i += (-1 if parseLeft else 1)
    if result == "":
        result = defaultValue
    return result

def DirectionParseList(startLetter, parsingText, endLetters, parseLeft = False, defaultValue: str = "0"):
    indicies = [match.start() for match in re.finditer(startLetter, parsingText)]
    results = []
    for index in indicies:
        results.append(DirectionParse(index, parsingText, endLetters, parseLeft, defaultValue))
    return results


class DiceRoller:

    # diceGroup, AdvantageRolls, Dice[2]
    diceList: list[list[list[int]]] = []
    result: list[int] = 0

    diceResultLabel: ctk.CTkLabel
    root: ctk.CTk

    timeSinceAnimationStart: float = 0
    targetFadeInText: str = ""

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.diceResultLabel = ctk.CTkLabel(root, font=ctk.CTkFont(size=int(30*settings["gui"]["diceResultSizeMul"])))
        self.diceResultLabel.place(relx=0.5, rely=0.5, anchor="center")
        self.diceResultLabel.configure(text="Please type your first dice throw :)")
        allKeyBinds.append(self.RollDiceKey)

    def TextFadeInUpdateLoop(self):
        self.timeSinceAnimationStart += 0.0025*len(self.targetFadeInText)*settings["animationSpeed"]
        
        text = self.targetFadeInText[:int(self.timeSinceAnimationStart)]
        text += RANDOM_TEXT[random.randrange(0,len(RANDOM_TEXT))]

        self.diceResultLabel.configure(text=text)

        if self.timeSinceAnimationStart < len(self.targetFadeInText):
            self.root.after(2, self.TextFadeInUpdateLoop)
        else:
            self.diceResultLabel.configure(text=self.targetFadeInText)
    def TextRandomNumbersLoop(self):

        numberIndicies = []
        for i, c in enumerate(self.targetFadeInText):
            if c in NUMBERS:
                numberIndicies.append(i)
        

        self.timeSinceAnimationStart += 0.01*len(numberIndicies)*settings["animationSpeed"]
        for i in range(0, int(self.timeSinceAnimationStart)):
            if len(numberIndicies) != 0:
                numberIndicies.pop(0)
        text = self.targetFadeInText
        for i in numberIndicies:
            text = text[:i] + NUMBERS[random.randrange(0,len(NUMBERS))] + text[i + 1:]
        
        self.diceResultLabel.configure(text=text)

        if len(numberIndicies) != 0:
            self.root.after(2, self.TextRandomNumbersLoop)

    def StartAnimation(self):
        self.targetFadeInText = ""
        for diceThrows in self.diceList:
            self.targetFadeInText += diceThrows.__str__() + "\n"
        self.targetFadeInText += self.result.__str__()
        #self.targetFadeInText = F"{self.diceList}: {self.result}"
        self.timeSinceAnimationStart = 0
        match settings["animation"]:
            case "QUICK":
                self.diceResultLabel.configure(text=self.targetFadeInText)
            case "FADE_IN":
                self.TextFadeInUpdateLoop()
            case "RANDOM_NUMBERS":
                self.TextRandomNumbersLoop()
    
    
    def RollDice(self, diceConfig):

        self.diceList = []
        self.result = []

        for i, diceConfigGroup in enumerate(diceConfig["dice"]):
            self.diceList.append([])
            advantageResult = 0
            advantage = diceConfig["advantage"][i]
            bonus = diceConfig["bonus"][i]
            for j in range(abs(advantage)+1):
                self.diceList[-1].append([])
                diceGroup = GetDiceFromDiceConfig(diceConfigGroup)
                groupResult = 0
                for dice in diceGroup:
                    for _ in range(dice[0]):
                        randomValue = random.randint(1, dice[1])
                        groupResult += randomValue
                        self.diceList[-1][-1].append(randomValue)
                groupResult += bonus
                    
                
                advantageResult = groupResult if j == 0 else max(advantageResult, groupResult) if advantage > 0 else min(advantageResult, groupResult)
            self.result.append(advantageResult)
            
        
        self.StartAnimation()
        # diceResults = []
        # for _ in range(abs(diceConfig["advantage"])+1):
        #     self.diceList.append([])
        #     diceResults.append(0)
        #     for i in range(diceConfig["dice"][0]):
        #         for i in range(random.randint(1,10)):
        #             random.randint(1,diceConfig["dice"][1])
        #         self.diceList[-1].append(random.randint(1,diceConfig["dice"][1]))
        #         diceResults[-1] += self.diceList[-1][-1]
        #     diceResults[-1] += diceConfig["bonus"]
        # if diceConfig["advantage"] > 0:
        #     self.result = max(diceResults)
        # else:
        #     self.result = min(diceResults)
        # self.StartAnimation()
        print("rolled dice with config:\n"+diceConfig.__str__())

    
    def RollDiceKey(self, event):
        if event.keysym == "Return":
            if searchManager.state != SearchManagerState.additionalBonus:
                if len(searchManager.matchingListDiceConfigs) == 0:
                    return
                self.RollDice(searchManager.matchingListDiceConfigs[0])
            else:
                operationNumber = int(DirectionParse(0, searchManager.currentSearch, "+-*/=", defaultValue=1))
                match searchManager.currentSearch[0]:
                    case "+":
                        self.result += operationNumber
                    case "-":
                        self.result -= operationNumber
                    case "*":
                        self.result *= operationNumber
                    case "/":
                        self.result //= operationNumber
                    case "=":
                        self.result = operationNumber
                self.StartAnimation()



class TabManager:

    currentSearchList: any
    currentSearchListIndex: int
    tabFrame: ctk.CTkFrame
    tabLabels: list[ctk.CTkLabel] = []


    def __init__(self, root: ctk.CTk):

        self.tabFrame = ctk.CTkFrame(root)
        self.tabFrame.place(relx=0, rely=0, anchor="nw", relwidth=1)

        for i, bind in enumerate(settings["binds"]):
            self.tabLabels.append(
                ctk.CTkLabel(self.tabFrame, text=settings["binds"][i]+" ("+str(i+1)+")", font=ctk.CTkFont(size=int(12*settings["gui"]["tabsSizeMul"])))
                )
            
            self.tabLabels[-1].pack(side="left", fill="x", padx=25)
        self.SetTabGraphics(0)

        self.currentSearchListIndex = 0
        self.currentSearchList = config[settings["binds"][0]]
        allKeyBinds.append(self.SetCurrentSearchListKey)
        

    def SetCurrentSearchList(self, letter: chr):
        number = int(letter)-1
        if number == -1:
            number = 9
        if number >= len(settings["binds"]):
            return
        self.currentSearchListIndex = number
        self.SetTabGraphics(number)
        print("changed tab to:", letter)
        self.currentSearchList = config[settings["binds"][number]]

    def SetTabGraphics(self, index: int):
        for i, tab in enumerate(self.tabLabels):
            if i == index:
                self.tabLabels[i].configure(text_color="red")
                continue
            self.tabLabels[i].configure(text_color="white")
        

    def SetCurrentSearchListKey(self, event):
        if event.keysym in NUMBERS and not searchManager.inSearch:
            self.SetCurrentSearchList(event.keysym)
        
class SearchManagerState(Enum):
    normal: int = 0
    customDice: int = 1
    additionalBonus: int = 2

class SearchManager:
    state = SearchManagerState.normal

    currentSearch: str = ""
    currentSearchLabel: ctk.CTkLabel
    inSearch: bool = False
    typingDisplayFrame: ctk.CTkFrame
    matchingListDiceConfigs: list = []

    searchedDiceConfigLabel: ctk.CTkLabel

    def __init__(self, root: ctk.CTk):
        self.typingDisplayFrame = ctk.CTkFrame(root)
        self.typingDisplayFrame.place(relx=-0.5, rely=0.5, anchor="center")
        self.frameColor = self.typingDisplayFrame._fg_color
        self.currentSearchLabel = ctk.CTkLabel(self.typingDisplayFrame, font=ctk.CTkFont(size=int(80*settings["gui"]["searchSizeMul"])), text="")
        self.currentSearchLabel.pack()

        self.searchedDiceConfigLabel = ctk.CTkLabel(root, text="", font=ctk.CTkFont(size=int(20*settings["gui"]["currentDiceSizeMul"])))
        self.searchedDiceConfigLabel.place(relx=0.5, rely=1, anchor="s")

        #self.typingDisplayFrame.configure(fg_color="transparent")
        allKeyBinds.append(lambda event: self.KeyPress(event))

    def SetFrameState(self, state: bool):
        if state:
            self.typingDisplayFrame.place(relx=0.5)
            self.currentSearchLabel.configure(text=self.currentSearch)
        else:
            self.typingDisplayFrame.place(relx=-0.5)
            self.currentSearchLabel.configure(text="")
            self.state = SearchManagerState.normal
        self.inSearch = state
        self.UpdateSearch()

    def UpdateSearch(self):
        match self.state:
            case SearchManagerState.normal:
                self.NormalStateSearch()
            case SearchManagerState.additionalBonus:
                self.currentSearchLabel.configure(text_color="blue")
            case SearchManagerState.customDice:                
                self.CustomDiceSearch()



    #TODO make better
    def CustomDiceSearch(self):
        self.currentSearchLabel.configure(text_color="purple")
        try:
            splitSearch = self.currentSearch.split(".")
            splitSearch.pop(0)

            bonusList: list[int] = []
            diceList: list[list[int]] = []
            advantageList: list[int] = []
            
            for search in splitSearch:
                diceInterp: list[int] = []
                bonusInterp: int = 0
                advantageInterp: int = 0

                bonusText = DirectionParseList("b", search, ".,dba", True, "0")
                diceCountText = DirectionParseList("d", search, ".,dba", True, "1")
                diceText = DirectionParseList("d", search, ".,dba", False, "4")
                advantageText = DirectionParseList("a", search, ".,dba", False, "0")


                bonusInterp = sum([int(x) for x in bonusText])
                advantageInterp = sum([int(x) for x in advantageText])
                for i, dice in enumerate(diceText):
                    diceInterp.append(int(diceCountText[i]))
                    diceInterp.append(int(dice))
                    pass
                if len(diceInterp) == 0: diceInterp = [1,4]
                bonusList.append(bonusInterp)
                diceList.append(diceInterp)
                advantageList.append(advantageInterp)
                
                #advantageList = [int(x) for x in bonusText]

                # bonusText = DirectionParse(search.find("b"), search, ".dbaq", True, "0")
                # diceCountText = DirectionParse(search.find("d"), search, ".dbaq", True, "1")
                # diceText = DirectionParse(search.find("d"), search, ".dbaq", False, "4")
                # advantageText = DirectionParse(search.find("a"), search, ".dbaq", False, "null")
            self.matchingListDiceConfigs = [{"name":"custom", "bonus":bonusList, "dice":diceList, "advantage": advantageList}]
            
            
        except:
            print("incorrect syntax")
            self.matchingListDiceConfigs = [{"name":"syntax error", "bonus":[0], "dice":[[1, 4]], "advantage": [0]}]
        #self.matchingListDiceConfigs = [{"name":"custom", "bonus":int(bonusText), "dice":[int(diceCountText), int(diceText)], "advantage": 0}]
        
        self.UpdateDiceConfigGraphic()

        
        
        

    def NormalStateSearch(self):
        if self.currentSearch == "":
            return
        searchList = config[settings["binds"][tabManager.currentSearchListIndex]]
        self.matchingListDiceConfigs = []
        for i, diceConfig in enumerate(searchList):
            match settings["searchType"]:
                case "STRICT":
                    if self.currentSearch == diceConfig["name"][:len(self.currentSearch)].lower():
                        self.matchingListDiceConfigs.append(deepcopy(diceConfig))
                case "FLEXIBLE":
                    if self.currentSearch in (diceConfig["name"].lower()):
                        self.matchingListDiceConfigs.append(deepcopy(diceConfig))
        print(self.matchingListDiceConfigs)
        if len(self.matchingListDiceConfigs) == 0:
            self.currentSearchLabel.configure(text_color="red")
            self.searchedDiceConfigLabel.configure(text="")
        else:
            self.currentSearchLabel.configure(text_color="green")
            self.UpdateDiceConfigGraphic()
            
    
    def UpdateDiceConfigGraphic(self):
        diceConfig = self.matchingListDiceConfigs[0]
        text = ""
        text += F"name: {diceConfig["name"]}\n"
        if diceConfig["bonus"] != 0:
            text += F"bonus: {diceConfig["bonus"]}\n"
        text += "dice: "
        for diceGroup in diceConfig["dice"]:
            text += "["
            for i in range(0,len(diceGroup)-1,2):
                text += F"{diceGroup[i]}d{diceGroup[i+1]},"
            text = text.strip(",")+"]"
        text += "\n"
        text += F"advantage: {diceConfig["advantage"]}\n"
        self.searchedDiceConfigLabel.configure(text=text)

            


    def AddLetter(self, letter: chr):
        self.currentSearch += letter
        self.SetFrameState(True)
        #self.typingDisplayFrame.configure(fg_color=self.frameColor)
        
        

    def RemoveLetter(self):
        self.currentSearch = self.currentSearch[:-1]
        self.SetFrameState(True)
        if len(self.currentSearch) == 0:
            self.SetFrameState(False)
    def ResetFrame(self):
        self.currentSearch = ""
        self.SetFrameState(False)
    def KeyPress(self, event):
        if (event.keysym in ALL_LETTERS and self.state != SearchManagerState.additionalBonus) or (self.state != SearchManagerState.normal and event.keysym in NUMBERS):
            if event.keysym == "space":
                self.AddLetter(" ")
                return
            self.AddLetter(event.keysym)
            #print(self.currentSearch)
        elif event.keysym == "Escape" or event.keysym == "Return":
            self.ResetFrame()
        elif event.keysym == "BackSpace":
            self.RemoveLetter()
        elif event.keysym == "period" or (event.keysym == "minus" and self.state == SearchManagerState.customDice):
            if self.state != SearchManagerState.customDice:
                self.currentSearch = ""
                self.state = SearchManagerState.customDice
            match event.keysym:
                case "period":
                    self.AddLetter(".")
                case "minus":
                    self.AddLetter("-")
        elif event.keysym == "comma":
            if self.state == SearchManagerState.customDice:
                self.AddLetter(",")
        elif event.keysym == "plus" or event.keysym == "asterisk" or event.keysym == "slash" or event.keysym == "minus" or event.keysym == "equal":
            self.currentSearch = ""
            self.state = SearchManagerState.additionalBonus
            match event.keysym:
                case "plus":
                    self.AddLetter("+")
                case "asterisk":
                    self.AddLetter("*")
                case "slash":
                    self.AddLetter("/")
                case "minus":
                    self.AddLetter("-")
                case "equal":
                    self.AddLetter("=")
        elif event.keysym == "Right" or event.keysym == "Left":
            if len(self.matchingListDiceConfigs) == 0: return
            for i in range(len(self.matchingListDiceConfigs[0]["advantage"])):
                #adv = adv + 1 if event.keysym == "Right" else adv - 1
                self.matchingListDiceConfigs[0]["advantage"][i] = self.matchingListDiceConfigs[0]["advantage"][i] + 1 if event.keysym == "Right" else self.matchingListDiceConfigs[0]["advantage"][i] - 1
                print(self.matchingListDiceConfigs[0]["advantage"][i])
            
            self.UpdateDiceConfigGraphic()
        else:
            print(event.keysym)




diceRoller = DiceRoller(root)
searchManager = SearchManager(root)
tabManager = TabManager(root)


root.mainloop()