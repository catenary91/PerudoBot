import discord
import random

from .betting import PerudoBetting

class PerudoPlayer():
    def __init__(self, itc: discord.Interaction):
        self.id = itc.user.id
        self.member = itc.user
        self.mention = itc.user.mention
        self.itc = itc
        self.num_dice = -1

    def roll_dice(self):
        self.dices = []
        for _ in range(self.num_dice):
            self.dices.append(random.choice([1, 2, 3, 4, 5, 6]))
        self.dices.sort()
    
    def dice_count(self, dice: int):
        if dice == 1:
            return self.dices.count(1)
        else:
            return self.dices.count(dice) + self.dices.count(1)

    def dice_info(self):
        return ''.join(PerudoBetting.dice_label[dice] for dice in self.dices)
    
    def __eq__(self, other):
        return self.id == other.id