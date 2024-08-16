import asyncio
import discord
from typing import Any

queue: dict[int, list[Any]] = {}
interactions: dict[int, discord.Interaction]
running: list[int] = []

async def run_queue(itc: discord.Interaction):
    id = itc.user.id
    if id not in queue:
        queue[id] = []
    running.append(id)

    print(f'queue started for {id}({itc.user.display_name})')

    while True:
        if len(queue[id]) > 0:
            func = queue[id].pop(0)
            if func == None:
                running.remove(id)
                print(f'queue ended for {id}({itc.user.display_name})')
                return
            await func(itc)
        await asyncio.sleep(0.5)
        
def stop_queue(id: int):
    if id not in queue:
        queue[id] = []
    queue[id].append(None)

def put_event(id: int, event):
    if id not in queue:
        queue[id] = []
    queue[id].append(event)

def queue_running(id: int):
    return id in running