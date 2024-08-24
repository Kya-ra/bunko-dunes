#!/usr/bin/env python3

import discord
from discord.ext import tasks
from datetime import datetime

#@tasks.loop(hours=24)
async def remove_guests(ctx):
    date = datetime.now()
    if date.day == 1:
        guild = ctx.guild
        guests = []
        guestrole = None
        for r in guild.roles:
            if r.name == "Guest":
                guestrole = r
                break
                
        if not guestrole:
            await ctx.send("Tried to remove Guest roles from all users, but no 'Guest' role was found on the server.")
            return
        
        # remove guest role here
        for member in guild.members:
            if guestrole in member.roles:
                await member.remove_roles(guestrole, reason="Automatic monthly Guest role removal")
                guests += [member]
                
        msg = "Monthly <@&"+str(guestrole.id)+"> role removal complete.\nRevoked from "+str(len(guests))+" guest(s):\n```"
        
        for guest in guests:
            if len(msg) > 1500:
                await ctx.send(msg+"```")
                msg = "```"
            msg += guest.display_name.ljust(20) + (guest.name + "#" + guest.discriminator) +"\n"
        await ctx.send(msg+"```")
        