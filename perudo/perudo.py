import discord
from discord import ui, app_commands
from discord.ext import commands

from .recruit import PerudoRecruitManager
from .game import PerudoGameManager


class Perudo(commands.Cog):
    recruits: dict[int, PerudoRecruitManager] = {}
    games: dict[int, PerudoGameManager] = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='페루도', description='새로운 페루도 게임을 모집합니다.')
    async def recruit(self, itc: discord.Interaction):
        if itc.channel_id in self.games and self.games[itc.channel_id].running:
            await itc.response.send_message('게임이 이미 진행 중입니다.', ephemeral=True)
            return
        
        if itc.channel_id in self.recruits:
            await itc.response.send_message('게임이 이미 모집 중입니다.', ephemeral=True)
            return
        
        await itc.response.defer()
        manager = PerudoRecruitManager(itc)
        self.recruits[itc.channel_id] = manager
        await manager.recruit(itc)

    @app_commands.command(name='시작', description='모집중인 페루도 게임을 시작합니다. 주사위의 개수를 선택해주세요.')
    @app_commands.choices(주사위=[
        app_commands.Choice(name='5개', value=5),
        app_commands.Choice(name='6개', value=6),
        app_commands.Choice(name='7개', value=7)
    ])
    async def start(self, itc: discord.Interaction, 주사위: int):
        if itc.channel_id not in self.recruits:
            await itc.response.send_message('모집 중인 게임이 없습니다.\n"/perudo" 명령어를 사용하여 새로운 게임을 모집해보세요.', ephemeral=True)
            return
        manager = self.recruits[itc.channel_id]

        if itc.user != manager.starter:
            await itc.response.send_message('게임을 모집한 사람만 시작할 수 있습니다.', ephemeral=True)
            return

        max_dice = 주사위

        if max_dice not in [4, 5, 6, 7]:
            await itc.response.send_message('주사위의 개수는 4개, 5개, 6개, 7개 중에 선택 가능합니다.', ephemeral=True)
            return

        await manager.delete_msg()
        game = PerudoGameManager(manager.players, max_dice)
        self.games[itc.channel_id] = game
        self.recruits.pop(itc.channel_id)
        await game.start(itc)


    @app_commands.command(name='취소', description='모집 중인 페루도 게임을 취소합니다.')
    async def cancel(self, itc: discord.Interaction):
        if itc.channel_id not in self.recruits:
            await itc.response.send_message('모집 중인 게임이 없습니다.\n"/perudo" 명령어를 사용하여 새로운 게임을 모집해보세요.', ephemeral=True)
            return
        manager = self.recruits[itc.channel_id]
        if itc.user != manager.starter:
            await itc.response.send_message('게임을 모집한 사람만 취소할 수 있습니다.', ephemeral=True)
            return

        await manager.delete_msg()
        await itc.response.send_message('게임이 취소되었습니다.')
        self.recruits.pop(itc.channel_id)

        