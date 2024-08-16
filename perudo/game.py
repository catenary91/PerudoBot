import discord

from .player import PerudoPlayer
from .betting import PerudoBetting, PerudoBettingManager

class PerudoGame:
    def __init__(self, players: list[PerudoPlayer], max_dice: int, callback):
        self.callback = callback
        self.max_dice = max_dice
        self.players = players
        self.starter = players[0]
        self.index = 0

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
        self.msg = None
        for msg in self.dice_messages:
            print(f'delete {msg.content}')
            await msg.delete()

        self.dice_messages.clear()
        self.current_betting = None

        self.roll_dice()
        description = '\nㅤ\n'.join([
            f'{itc.user.mention}님의 베팅 차례입니다.',
            f'**현재 베팅:ㅤ{self.current_betting}**' if self.current_betting else ''
        ])
        await self.update_embed(itc, description)

        for player in self.players:
            msg = await player.itc.followup.send(player.dice_info(), ephemeral=True)
            self.dice_messages.append(msg)

        await self.start_betting(itc)
        
    async def start_betting(self, itc: discord.Interaction):
        description = '\nㅤ\n'.join([
            f'{itc.user.mention}님의 베팅 차례입니다.',
            f'**현재 베팅:**ㅤ{self.current_betting}' if self.current_betting else '',
        ])
        await self.update_embed(itc, description)

        await PerudoBettingManager(self.current_betting).start(itc, self.finished_betting)
        
    async def finished_betting(self, itc: discord.Interaction, betting: PerudoBetting | str):
        if isinstance(betting, PerudoBetting):
            self.current_betting = betting
            self.index = (self.index + 1) % len(self.players)
            
            await self.start_betting(self.current_player().itc)
            return

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
        gain_dice = correct and betting == 'equal' and winner.num_dice < self.max_dice

        betting_str = {'equal': '정확', 'less': '적다'}[betting]
        description = '\nㅤ\n'.join([
            f'{itc.user.mention}님이 {self.current_betting}에 대해 "{betting_str}"(을)를 불렀습니다.',
            f'{self.current_betting.dice_str()}은(는) `{cnt}개`였습니다!',
            f'{loser.mention}님이 주사위 1개를 잃었습니다.',
            f'{winner.mention}님이 주사위 1개를 얻었습니다.' if gain_dice else ''
        ])

        await self.update_embed(itc, description, True)

        # actual dice change is after the embed
        if gain_dice:
            winner.num_dice += 1
        loser.num_dice -= 1

        if loser.num_dice == 0:
            await itc.channel.send(f'{loser.mention}님이 탈락했습니다.')
            self.players.remove(loser)
            await self.callback(itc)
            return

        self.index = self.players.index(loser)
        await self.start(loser.itc)
        

    async def update_embed(self, itc: discord.Interaction, description: str, reveal_dice: bool = False):
        embed = discord.Embed(
            title='페루도', 
            description=description, 
            color=0x450707
        )
        embed.add_field(
            name='참가자', 
            value='\n'.join(p.mention for p in self.players)
        )
        embed.add_field(
            name='ㅤㅤ주사위 개수', 
            value='\n'.join(f'ㅤㅤ{p.num_dice}개' for p in self.players)
        )

        if not reveal_dice:
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


class PerudoGameManager:
    def __init__(self, players: list[PerudoPlayer], max_dice: int):
        self.players = players
        self.max_dice = max_dice
        self.running = False
        self.game = None
        
    async def start(self, itc: discord.Interaction):
        self.running = True
        for player in self.players:
            player.num_dice = self.max_dice

        self.game = PerudoGame(self.players, self.max_dice, self.round_finished)
        await itc.response.defer()
        await self.game.start(itc)

    async def round_finished(self, itc: discord.Interaction):
        if len(self.players) > 2:
            self.game = PerudoGame(self.players, self.max_dice, self.round_finished)
            await self.game.start(itc)
            return
        
        self.running = False
        winner = self.players[0].member
        embed = discord.Embed(title='페루도', description=f'{winner.mention}님이 우승하였습니다!', color=0x450707)
        embed.set_image(url=winner.display_avatar.url)

        await itc.channel.send(embed=embed)

