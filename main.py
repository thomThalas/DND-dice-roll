import customtkinter as ctk
import json
import random
from dataclasses import dataclass
from enum import Enum


root = ctk.CTk()

#root.resizable(False, False)
root.geometry("800x800")



ALL_LETTERS = [
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z","space"
]


NUMBERS = ["1","2","3","4","5","6","7","8","9","0"]

config = {}

with open("./config.json", "r") as f:
    config = json.loads(f.read())

settings = config["settings"]


allKeyBinds: list = []
def KeyPressed(event):
    for f in allKeyBinds:
        f(event)
root.bind("<Key>", KeyPressed)



class DiceRoller:

    diceResultLabel: ctk.CTkLabel

    def __init__(self, root: ctk.CTk):
        print("weee")
        self.diceResultLabel = ctk.CTkLabel(root, font=ctk.CTkFont(size=30))
        self.diceResultLabel.place(relx=0.5, rely=0.5, anchor="center")
        self.diceResultLabel.configure(text="Please type your first dice throw :)")
        allKeyBinds.append(self.RollDiceKey)

    def RollDice(self, diceConfig):
        sum = 0
        for i in range(diceConfig["dice"][0]):
            random.randint(1,diceConfig["dice"][1])
            random.randint(1,diceConfig["dice"][1])
            random.randint(1,diceConfig["dice"][1])
            sum += random.randint(1,diceConfig["dice"][1])
        sum += diceConfig["bonus"]
        self.diceResultLabel.configure(text=sum)
        print("rolled dice with config:\n"+diceConfig.__str__())
    
    def RollDiceKey(self, event):
        if event.keysym == "Return":
            if len(searchManager.matchingListDiceConfigs) == 0:
                return
            self.RollDice(searchManager.matchingListDiceConfigs[0])



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
                ctk.CTkLabel(self.tabFrame, text=settings["binds"][i]+" ("+str(i+1)+")")
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
        self.currentSearchLabel = ctk.CTkLabel(self.typingDisplayFrame, font=ctk.CTkFont(size=80))
        self.currentSearchLabel.pack()

        self.searchedDiceConfigLabel = ctk.CTkLabel(root, text="", font=ctk.CTkFont(size=20))
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
                print("additionalBonus")
            case SearchManagerState.customDice:                
                self.CustomDiceSearch()
                print("customDice")


    def DirectionParse(self, startIndex, parsingText, endLetters, parseLeft = False, defaultValue: str = "0"):
        result = ""
        i = startIndex + (-1 if parseLeft else 1)
        if i >= 0:
            while i < len(parsingText) and parsingText[i] not in endLetters:
                if parseLeft:
                    result = parsingText[i] + result
                else:
                    result += parsingText[i]
                
                i += (-1 if parseLeft else 1)
        if result == "":
            result = defaultValue
        return result

    def CustomDiceSearch(self):
        self.currentSearchLabel.configure(text_color="purple")
        if self.currentSearch == ".":
            return
        try:
            bonusText = self.DirectionParse(self.currentSearch.find("b"), self.currentSearch, ".", True, "0")
            diceCountText = self.DirectionParse(self.currentSearch.find("d"), self.currentSearch, ".b", True, "1")
            diceText = self.DirectionParse(self.currentSearch.find("d"), self.currentSearch, ".b", False, "4")
            self.matchingListDiceConfigs = [{"name":"custom", "bonus":int(bonusText), "dice":[int(diceCountText), int(diceText)]}]
        except:
            print("incorrect syntax")
            self.matchingListDiceConfigs = [{"name":"syntax error", "bonus":0, "dice":[1, 4]}]
        
        self.UpdateDiceConfigGraphic()

        
        
        

    def NormalStateSearch(self):
        if self.currentSearch == "":
            return
        searchList = config[settings["binds"][tabManager.currentSearchListIndex]]
        self.matchingListDiceConfigs = []
        for i, diceConfig in enumerate(searchList):
            if self.currentSearch == diceConfig["name"][:len(self.currentSearch)].lower():
                self.matchingListDiceConfigs.append(diceConfig)
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
        text += F"bonus: {diceConfig["bonus"]}\n"
        text += F"dice: {diceConfig["dice"][0]}d{diceConfig["dice"][1]}\n"

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
        elif event.keysym == "period":
            self.currentSearch = ""
            self.state = SearchManagerState.customDice
            #self.SetFrameState(True)
            self.AddLetter(".")
        else:
            
            print(event.keysym)




diceRoller = DiceRoller(root)
searchManager = SearchManager(root)
tabManager = TabManager(root)


root.mainloop()