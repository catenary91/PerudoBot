import discord
from discord import app_commands
from discord.ext import commands

from .recruit import PerudoRecruitManager
from .game import PerudoGame
    

class Perudo(commands.Cog):
    games: dict[int, PerudoGame] = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='perudo', description='Start a new perudo game')
    async def recruit(self, itc: discord.Interaction):
        if itc.channel_id in self.games and (self.games[itc.channel_id].recruiting or self.games[itc.channel_id].running):
            await itc.response.send_message('게임이 이미 진행 중입니다.', ephemeral=True)
            return
        
        recruit_manager = PerudoRecruitManager()
        await recruit_manager.recruit(itc, self.start)
    
    async def start(self, itc: discord.Interaction, members: list[discord.Member], max_dice: int):
        game = PerudoGame(members, max_dice)
        self.games[itc.channel_id] = game
        await game.start(itc)
