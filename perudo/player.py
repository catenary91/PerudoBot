import discord

class PerudoPlayer():
    def __init__(self, member: discord.Member, max_dice: int):
        self.member = member
        self.max_dice = max_dice
        self.mention = member.mention
        self.dice = max_dice
