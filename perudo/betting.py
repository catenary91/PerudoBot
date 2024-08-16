import discord
from discord import ui

class PerudoBetting:
    dice_label = {1: ':skull_crossbones:', 2: ':two:', 3: ':three:', 4: ':four:', 5: ':five:', 6: ':six:'}

    def __init__(self, num: int, dice: int):
        self.num = num
        self.dice = dice

    def get_value(self):
        if self.dice == 1:
            return self.num * 200 - 10
        else:
            return self.num * 100 + self.dice

    def dice_str(self):
        return self.dice_label[self.dice]

    def __lt__(self, other):
        if self.num == other.num:
            return self.dice < other.dice

    def __eq__(self, other):
        return isinstance(other, PerudoBetting) and self.num == other.num and self.dice == other.dice
    
    def __str__(self):
        return f'{self.dice_label[self.dice]} `{self.num}개`'


def flatten(xss):
    return [x for xs in xss for x in xs]        

class PerudoBettingManager:
    num_labels = flatten([f'{n}', f'페루도 {(n+1)//2}', f'{n+1}'] for n in range(1, 21, 2))
    num_options = [discord.SelectOption(label=f'{l}개', value=l) for l in num_labels]
    dice_options = [discord.SelectOption(label=str(n)) for n in range(2, 7)]

    def __init__(self, prev: PerudoBetting | None = None):
        self.prev = prev

    async def start(self, itc: discord.Interaction, thread: discord.Thread, callback):
        self.thread = thread
        self.callback = callback
        self.view = ui.View()

        if self.prev == None: # first betting
            num_options = self.num_options[:20]
        elif self.prev.dice == 1: # previous betting is perudo
            idx = self.num_labels.index(str(self.prev.num * 2))
            num_options = self.num_options[idx:idx+20]
        elif self.prev.dice == 6: # previous betting is 6
            idx = self.num_labels.index(str(self.prev.num)) + 1
            num_options = self.num_options[idx:idx+20]    
        else:
            idx = self.num_labels.index(str(self.prev.num))
            num_options = self.num_options[idx:idx+20]

        self.num_select = ui.Select(placeholder='주사위 개수', options=num_options, row=0)

        self.num_select.callback = self.select_num
        self.view.add_item(self.num_select)
        
        if self.prev:
            self.less_btn = ui.Button(label='적다', row=2)
            self.less_btn.callback = self.less
            self.equal_btn = ui.Button(label='정확', row=2)
            self.equal_btn.callback = self.equal
            self.view.add_item(self.less_btn)
            self.view.add_item(self.equal_btn)

        self.msg = await itc.followup.send('베팅을 선택해주세요.', view=self.view, ephemeral=True, wait=True, thread=self.thread)

    async def select_num(self, itc: discord.Interaction):
        num_select = self.num_select.values[0]
        if num_select.startswith('페루도'): # betting finished
            num = int(num_select[4:])
            dice = 1
            await self.msg.delete()
            await self.callback(itc, PerudoBetting(num, dice))
            return
        
        self.num_select.placeholder = self.num_select.values[0] + '개' 

        current_num = int(num_select)
        if self.prev and self.prev.num == current_num and self.prev.dice in [2, 3, 4, 5]:   
            self.dice_select = ui.Select(placeholder='주사위 눈', options=self.dice_options[self.prev.dice-1:], row=1)
        else:
            self.dice_select = ui.Select(placeholder='주사위 눈', options=self.dice_options, row=1)

        self.dice_select.callback = self.select_dice
        self.view.clear_items()
        self.view.add_item(self.num_select)
        self.view.add_item(self.dice_select)
        
        if self.prev:
            self.view.add_item(self.less_btn)
            self.view.add_item(self.equal_btn)

        await itc.response.edit_message(content='주사위의 눈을 선택해주세요.', view=self.view)

    async def select_dice(self, itc: discord.Interaction):
        num = int(self.num_select.values[0])
        dice = int(self.dice_select.values[0])

        await self.msg.delete()
        await self.callback(itc, PerudoBetting(num, dice))

    async def less(self, itc: discord.Interaction):
        await self.msg.delete()
        await self.callback(itc, 'less')

    async def equal(self, itc: discord.Interaction):
        await self.msg.delete()
        await self.callback(itc, 'equal')
