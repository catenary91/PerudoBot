import discord
import random

from .betting import PerudoBetting

class PerudoPlayer():
    def __init__(self, member: discord.Member, max_dice: int):
        self.member = member
        self.mention = member.mention
        self.id = member.id
        self.max_dice = max_dice
        self.num_dice = max_dice

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