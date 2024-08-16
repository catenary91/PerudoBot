import discord
from discord import ui

class PerudoBetting:
    def __init__(self, num=-1, dice=-1):
        self.num = num
        self.dice = dice
    
    def is_valid(self):
        return self.num != -1 and self.dice != -1

    def get_value(self):
        if self.dice == 1:
            return self.num * 200 - 10
        else:
            return self.num * 100 + self.dice

    def __lt__(self, other):
        if self.num == other.num:
            return self.dice < other.dice
        
class PerudoBettingView(ui.View):
    def __init__(self, start_betting: PerudoBetting):
        self.start_betting = start_betting

    