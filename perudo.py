from typing import Tuple

import discord
from discord import ui, app_commands
from discord.ext import commands

class PerudoGame():
    def __init__(self, starter: discord.Member, guild: discord.Guild, channel: discord.TextChannel):
        self.starter = starter
        self.guild = guild
        self.channel = channel
        
        self.recruiting = True
        self.running = False
        self.members = [self.starter]


    def add_member(self, member: discord.Member) -> bool:
        if member in self.members:
            return False
        
        self.members.append(member)
        return True
    
    def del_member(self, member: discord.Member) -> bool:
        if not member in self.members:
            return False
        
        self.members.remove(member)
        return True
    
    def start(self, max_dice: int):
        self.max_dice = max_dice
        self.index = 0
        self.recruiting = False
        self.running = True
        self.dice_num = [self.max_dice for _ in self.members]

    def current_player(self):
        return self.members[self.index]
    
class Perudo(commands.Cog):
    games: dict[int, PerudoGame] = {}

    def __init__(self, bot):
        self.bot = bot
    
    recruit_itc_msg: dict[int, Tuple[discord.Interaction, discord.WebhookMessage]] = {}
    async def update_recruit_embed(self, channel_id: int):
        r_itc, _ = self.recruit_itc_msg[channel_id]
        game = self.games[channel_id]
        
        embed = (await r_itc.original_response()).embeds[0]
        embed.remove_field(1)
        embed.add_field(
            name='현재 멤버', 
            value='\n'.join([m.mention for m in game.members]), 
            inline=True
        )
        await r_itc.edit_original_response(embed=embed)

    async def delete_recruit_msg(self, channel_id: int):
        r_itc, msg = self.recruit_itc_msg[channel_id]
        await r_itc.delete_original_response()
        await msg.delete()


    game_itc: dict[int, discord.Interaction] = {}
    async def update_game_embed(self, itc: discord.Interaction, description):
        game = self.games[itc.channel_id]
        embed = discord.Embed(title='페루도', description=description, color=0x450707)
        embed.add_field(name='참가자', value='\n'.join([m.mention for m in game.members]))
        embed.add_field(name='\t주사위 개수', value='\t' + '\n\t'.join(f'{n}개' for n in game.dice_num))
        embed.add_field(
            name='   현재 차례', 
            value='\n'.join(
                '   ✅' if m == game.current_player() else ''
                for m in game.members
            )
        )

        if itc.channel_id in self.game_itc:
            g_itc = self.game_itc[itc.channel_id]
            g_itc.edit_original_response(embed=embed)
        else:
            await itc.response.send_message(embed=embed)
            self.game_itc[itc.channel_id] = itc


    @app_commands.command(name='perudo', description='Start a new perudo game')
    async def start_perudo(self, itc: discord.Interaction):
        if itc.channel_id in self.games and (self.games[itc.channel_id].recruiting or self.games[itc.channel_id].running):
            await itc.response.send_message('게임이 이미 진행 중입니다.', ephemeral=True)
            return
        
        start_button = ui.Button(style=discord.ButtonStyle.green, label='시작')
        start_button.callback = self.start_game

        cancel_button = ui.Button(style=discord.ButtonStyle.gray, label='게임 취소')
        cancel_button.callback = self.cancel_game

        apply_button = ui.Button(style=discord.ButtonStyle.primary, label='참가')
        apply_button.callback = self.enter_game
        
        cancel_apply_button = ui.Button(style=discord.ButtonStyle.danger, label='나가기')
        cancel_apply_button.callback = self.cancel_apply

        view = ui.View()
        view.add_item(apply_button)
        view.add_item(cancel_apply_button)

        control_view = ui.View()
        control_view.add_item(start_button)
        control_view.add_item(cancel_button)

        embed = discord.Embed(title='페루도', description=f'{itc.user.mention}님이 새로운 페루도 게임을 모집합니다.', color=0x450707)
        embed.add_field(name='최소 인원', value='2명', inline=True)
        embed.add_field(name='현재 멤버', value=f'{itc.user.mention}', inline=True)
        
        await itc.response.send_message(embed=embed, view=view)
        
        msg = await itc.followup.send(view=control_view, ephemeral=True)

        self.games[itc.channel_id] = PerudoGame(itc.user, itc.guild, itc.channel)
        self.recruit_itc_msg[itc.channel_id] = itc, msg


    async def start_game(self, itc: discord.Interaction):
        game = self.games[itc.channel.id]
        
        if len(game.members) == 1:
            await itc.response.send_message('게임의 최소 인원은 2명입니다.', ephemeral=True)
            return
        
        if game.starter != itc.user:
            await itc.response.send_message('게임을 모집한 사람만 시작할 수 있습니다.', ephemeral=True)
            return
        
        dice_select = ui.Select(
            placeholder='선택', 
            options=[
                discord.SelectOption(label='5개', value='5'),
                discord.SelectOption(label='6개', value='6'),
                discord.SelectOption(label='7개', value='7'),
            ]
        )

        async def callback(_itc: discord.Interaction):
            game.start(int(dice_select.values[0]))
            await self.delete_recruit_msg(_itc.channel_id)
            await itc.delete_original_response()
            await self.update_game_embed(_itc, f'현재 {game.current_player().mention}님의 차례입니다.')

        dice_select.callback = callback
        
        view = ui.View()
        view.add_item(dice_select)

        await itc.response.send_message('인당 주사위의 개수를 선택해주세요', view=view, ephemeral=True)


    async def enter_game(self, itc: discord.Interaction):
        game = self.games[itc.channel_id]

        if game.add_member(itc.user):
            await self.update_recruit_embed(itc.channel_id)
            await itc.response.send_message('게임에 참가했습니다.', ephemeral=True)
        else:
            await itc.response.send_message('이미 게임에 참여중입니다.', ephemeral=True)
        

    async def cancel_apply(self, itc: discord.Interaction):
        game = self.games[itc.channel_id]
        
        if game.starter == itc.user:
            await itc.response.send_message('게임을 모집한 사람은 나갈 수 없습니다.', ephemeral=True)
            return

        if game.del_member(itc.user):
            await self.update_recruit_embed(itc.channel_id)
            await itc.response.send_message(f'게임 참가를 취소했습니다.')
        else:
            await itc.response.send_message('게임에 참여중이 아닙니다.', ephemeral=True)


    async def cancel_game(self, itc: discord.Interaction):
        game = self.games[itc.channel_id]

        if itc.user.id == game.starter.id:
            await itc.channel.send('게임이 취소되었습니다.')
            await self.delete_recruit_msg(itc.channel_id)
            del self.games[itc.channel_id]
        
        else:
            await itc.response.send_message('게임을 모집한 사람만 취소할 수 있습니다.', ephemeral=True)
