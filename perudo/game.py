import discord
from discord import Interaction, ui

from .player import PerudoPlayer
from .betting import PerudoBetting, PerudoBettingManager
from event_queue import run_queue, put_event, queue_running

class PerudoGame:
    def __init__(self, members: list[discord.Member], max_dice: int):
        self.max_dice = max_dice
        self.players = [PerudoPlayer(m, max_dice) for m in members]
        self.starter = members[0]
        self.index = 0

        self.current_betting = None
        self.msg = None
        self.dice_messages = []
    
    def get_player(self, member: discord.Member):
        for p in self.players:
            if p.member == member:
                return p

    def current_player(self):
        return self.players[self.index]
    
    def roll_dice(self):
        for p in self.players:
            p.roll_dice()

    async def start(self, itc: discord.Interaction):
        await itc.response.defer()
        self.roll_dice()

        for player in self.players:
            put_event(player.id, self.show_dice)
        
        await self.start_betting(itc)

        await run_queue(itc)

    async def start_betting(self, itc: discord.Interaction):
        description = '\n'.join([
            f'{itc.user.mention}님의 베팅 차례입니다.\nㅤ',
            f'**현재 베팅:ㅤ{self.current_betting}**\nㅤ' if self.current_betting else ''
        ])
        await self.update_embed(itc, description)
        await PerudoBettingManager(self.current_betting).start(itc, self.finished_betting)
        
    async def finished_betting(self, itc: discord.Interaction, betting: PerudoBetting | str):
        if betting == 'less' or betting == 'equal':
            cnt = 0
            for p in self.players:
                cnt += p.dice_count(self.current_betting.dice)

            # check if the betting was correct
            if betting == 'less':
                correct = cnt < self.current_betting.num
            else:
                correct = cnt == self.current_betting.num

            # set the winner and the loser
            if correct:
                winner = self.current_player()
                loser = self.players[(self.index - 1) % len(self.players)]
            else:
                winner = self.players[(self.index - 1) % len(self.players)]
                loser = self.current_player()

            # if EQUAL betting was correct, the player gets a dice
            if correct and betting == 'equal' and winner.num_dice < self.max_dice:
                winner.num_dice += 1
                gain_dice = True
            else:
                gain_dice = False

            loser.num_dice -= 1

            betting_str = {'equal': '정확', 'less': '적다'}[betting]
            description = '\nㅤ\n'.join([
                f'{itc.user.mention}님이 {self.current_betting}에 대해 "{betting_str}"(을)를 불렀습니다.',
                f'{self.current_betting.dice_str()}은(는) {cnt}개였습니다!',
                f'{loser.mention}님이 주사위 1개를 잃었습니다.',
                f'{winner.mention}님이 주사위 1개를 얻었습니다.' if gain_dice else ''
                f'ㅤ'
            ])

            await self.update_embed(itc, description, True)
            self.msg = None

            put_event(loser.id, self.start_over)

            return
        
        self.current_betting = betting
        self.index = (self.index + 1) % len(self.players)
        
        put_event(self.current_player().id, self.start_betting)
        

    async def update_embed(self, itc: discord.Interaction, description: str, show_dice: bool = False):
        embed = discord.Embed(title='페루도', description=description, color=0x450707)
        embed.add_field(
            name='참가자', 
            value='\n'.join(p.mention for p in self.players)
        )
        embed.add_field(
            name='ㅤㅤ주사위 개수', 
            value='\n'.join(f'ㅤㅤ{p.num_dice}개' for p in self.players)
        )

        if not show_dice:
            embed.add_field(
                name='ㅤㅤ현재 차례', 
                value='\n'.join(
                    'ㅤㅤ✅' if m == self.current_player() else 'ㅤ'
                    for m in self.players
                )
            )
        else:
            embed.add_field(
                name='ㅤㅤ주사위',
                value='\n'.join(
                    f'ㅤㅤ{player.dice_info()}'
                    for player in self.players
                )
            )
    
        if self.msg:
            await self.msg.edit(embed=embed)
        else:
            await itc.followup.send(embed=embed)
            async for msg in itc.channel.history(limit=1):
                self.msg = msg

    async def show_dice(self, itc: discord.Interaction):
        player = self.get_player(itc.user)
        # self.dice_messages.append(await itc.followup.send(f'{itc.user.mention}님의 주사위 :\n\n{player.dice_info()}', ephemeral=True))
        # self.dice_messages.append(await itc.followup.send(f'{itc.user.mention}님의 주사위', ephemeral=True))
        self.dice_messages.append(await itc.followup.send(player.dice_info(), ephemeral=True))

    async def start_over(self, itc: discord.Interaction):
        for msg in self.dice_messages:
            await msg.delete()
        self.dice_messages.clear()

        self.roll_dice()

        await self.update_embed(itc, f'{itc.user.mention}님의 베팅 차례입니다.\nㅤ')
        for player in self.players:
            put_event(player.id, self.show_dice)

        await PerudoBettingManager(self.current_betting).start(itc, self.finished_betting)


class PerudoGameManager:
    def __init__(self, members: list[discord.Member], max_dice: int):
        self.members = members
        self.max_dice = max_dice
        self.running = False
        self.game = None
        
    async def start(self, itc: discord.Interaction):
        self.running = True
        self.game = PerudoGame(self.members, self.max_dice)
        self.game.start()
        