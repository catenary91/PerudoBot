import discord
from discord import ui

from .player import PerudoPlayer
from .betting import PerudoBetting, PerudoBettingModal

class PerudoGame:
    def __init__(self, members: list[discord.Member], max_dice):
        self.max_dice = max_dice
        self.players = [PerudoPlayer(m, max_dice) for m in members]
        self.starter = members[0]
        self.index = 0
        self.tmp_msg = None

        self.betting = PerudoBetting()
    
    def current_player(self):
        return self.players[self.index]
    
    def create_embed(self, description):
        embed = discord.Embed(title='페루도', description=description, color=0x450707)
        embed.add_field(name='참가자', value='\n'.join([p.mention for p in self.players]))
        embed.add_field(name='\t주사위 개수', value='\t' + '\n\t'.join(f'{n}개' for n in self.dice_num))
        embed.add_field(
            name='\t현재 차례', 
            value='\n'.join(
                '\t✅' if m == self.current_player() else ''
                for m in self.members
            )
        )
        return embed

    async def start(self, itc: discord.Interaction):
        embed = self.create_embed()

        await itc.response.send_message(embed=embed)

        btn = ui.Button(style=discord.ButtonStyle.gray, label='베팅')
        btn.callback = self.show_betting_modal
        view = ui.View()
        view.add_item(btn)
        self.tmp_msg = await itc.followup.send('아래 버튼을 눌러 주사위를 베팅해주세요.', view=view, ephemeral=True)

    async def show_betting_modal(self, itc: discord.Interaction):
        modal = PerudoBettingModal()
