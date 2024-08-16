import discord
from discord import ui

from .player import PerudoPlayer

class PerudoRecruitManager:
    def __init__(self, itc: discord.Interaction):
        self.starter = itc.user
        self.members = [itc.user]
        self.players = [PerudoPlayer(itc)]

    async def recruit(self, itc: discord.Interaction):
        embed = self.create_embed()
        apply_btn = ui.Button(label='참가', style=discord.ButtonStyle.primary)
        apply_btn.callback = self.apply
        apply_cancel_btn = ui.Button(label='나가기', style=discord.ButtonStyle.danger)
        apply_cancel_btn.callback = self.cancel_apply
        view = ui.View()
        view.add_item(apply_btn)
        view.add_item(apply_cancel_btn)

        self.msg = await itc.followup.send(embed=embed, view=view)
        
    def create_embed(self):
        embed = discord.Embed(title='페루도', description=f'{self.starter.mention}님이 새로운 페루도 게임을 모집합니다.', color=0x450707)
        embed.add_field(name='최소 인원', value='2명', inline=True)
        embed.add_field(
            name='현재 멤버', 
            value='\n'.join(m.mention for m in self.members), 
            inline=True
        )
        return embed

    async def apply(self, itc: discord.Interaction):
        if itc.user in self.members:
            await itc.response.send_message('이미 게임에 참여중입니다.', ephemeral=True)
        else:
            self.members.append(itc.user)
            self.players.append(PerudoPlayer(itc))
            await itc.message.edit(embed=self.create_embed())
            await itc.response.defer()
    
    async def cancel_apply(self, itc: discord.Interaction):
        if self.starter == itc.user:
            await itc.response.send_message('게임을 모집한 사람은 나갈 수 없습니다.', ephemeral=True)
            return

        if itc.user in self.members:
            self.members.remove(itc.user)
            self.players.remove(PerudoPlayer(itc))
            await itc.response.edit_message(embed=self.create_embed())

        else:
            await itc.response.send_message('게임에 참여중이 아닙니다.', ephemeral=True)

    async def delete_msg(self):
        await self.msg.delete()
        