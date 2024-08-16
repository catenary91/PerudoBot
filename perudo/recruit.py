import discord
from discord import ui

class PerudoRecruitView(ui.View):
    def __init__(self, starter: discord.Member, callback):
        super().__init__(timeout=None)
        self.starter = starter
        self.members = [starter]
        self.start = callback

    def create_embed(self):
        embed = discord.Embed(title='페루도', description=f'{self.starter.mention}님이 새로운 페루도 게임을 모집합니다.', color=0x450707)
        embed.add_field(name='최소 인원', value='2명', inline=True)
        embed.add_field(
            name='현재 멤버', 
            value='\n'.join(m.mention for m in self.members), 
            inline=True
        )
        return embed

    @discord.ui.button(label='참가', style=discord.ButtonStyle.primary)
    async def apply(self, itc: discord.Interaction, button: ui.Button):

        if itc.user in self.members:
            await itc.response.send_message('이미 게임에 참여중입니다.', ephemeral=True)
        else:
            self.members.append(itc.user)
            await itc.message.edit(embed=self.create_embed())
            await itc.response.send_message('게임에 참가했습니다.', ephemeral=True)

    
    @discord.ui.button(label='나가기', style=discord.ButtonStyle.danger)
    async def cancel_apply(self, itc: discord.Interaction, button: ui.Button):
        if self.starter == itc.user:
            await itc.response.send_message('게임을 모집한 사람은 나갈 수 없습니다.', ephemeral=True)
            return

        if itc.user in self.members:
            self.members.remove(itc.user)
            await itc.message.edit(embed=self.create_embed())
            await itc.response.send_message(f'게임 참가를 취소했습니다.')
        else:
            await itc.response.send_message('게임에 참여중이 아닙니다.', ephemeral=True)

    @discord.ui.button(label='시작', style=discord.ButtonStyle.green, row=1)
    async def start(self, itc: discord.Interaction, button: ui.Button):
        if self.starter != itc.user:
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
        async def start(itc: discord.Interaction):
            await self.start(itc, self.members, int(dice_select.values[0]))
        dice_select.callback = start

        view = ui.View()
        view.add_item(dice_select)

        await itc.response.send_message('주사위의 개수를 선택해주세요', view=view, ephemeral=True)

    @discord.ui.button(label='게임 취소', style=discord.ButtonStyle.gray, row=1)
    async def cancel(self, itc: discord.Interaction, button: ui.Button):
        if self.stater != itc.user:
            await itc.response.send_message('게임을 모집한 사람만 취소할 수 있습니다.', ephemeral=True)
            return

        await itc.message.delete()

class PerudoRecruitManager:
    async def recruit(self, itc: discord.Interaction, callback):
        view = PerudoRecruitView(itc.user, callback)
        embed = view.create_embed()

        await itc.response.send_message(embed=embed, view=view)

