#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import re
import ast
import random
from zalgo_text import zalgo
from dotenv import load_dotenv

import gamers_logo_change

ADMIN_ROLE="Committee"
MEMBER_ROLE="DU Gamers Member"
MAX_DICE_PER_ROLL = 100

GAMERS_GUILD_ID=370910745342509066
SECRET_BOT_CHANNEL_ID=687267382011625499

advanced_guilds = ["DU Gamers","pizzabotics test server"]
confirmation_token = ""
pending_command = ""
safe_roles = ["Committee", "Committee.", "Server Administration", "Guest", "Service bots", "Ambassador", "Admin"]

# Bunko source code
# Discord bot for DU Gamers
# Original code by Maghnus (Ferrus), adapted by Adam (Pizza, github: rathdrummer)


class Bunko(commands.Bot):
    gamers_guild = None
    gamers_bot_channel = None

    async def gamers(self):
        if self.gamers_guild == None:
            self.gamers_guild = self.get_guild(GAMERS_GUILD_ID)
        return self.gamers_guild

    async def bot_channel(self):
        g = await self.gamers()
        return await g.fetch_channel(SECRET_BOT_CHANNEL_ID)

    async def send_embed(self, ctx, author_url=None, url=None, title="DU Gamers", description="", color=0x9f3036, thumbnail=None, fieldname=None, fieldvalue="\u200b", author=None, author_icon=None):
    	e = discord.Embed(title=title, url=url, description=description, color=color)
    	if author:
    		e.set_author(name=author, icon_url=author_icon, url=author_url)
    	if thumbnail:
    		e.set_thumbnail(url=thumbnail)
    	if fieldname:
    		if fieldvalue:
    			e.add_field(name=fieldname, value=fieldvalue)
    		else:
    			e.add_field(name=fieldname)
    	await ctx.send(embed=e)



# Load environment variabpassles, to keep Discord bot token distinct from this file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = Bunko(intents=intents, command_prefix="+")

# Checks - for admin-level functions
def is_in_guild(guild_id):
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == guild_id
    return commands.check(predicate)
    message = ctx.message
    msg = message.content

async def verify_admin(ctx):
    for role in [r.name for r in ctx.author.roles]:
        if role == ADMIN_ROLE:
            return True
    await ctx.send("Sorry, admin only")
    return False

def parse (command, outputString):
    print(command)
    if command.isnumeric():
        print(command)
        return int(command)
    if '(' in command:
      index = command.rfind('(')
      left = command[:index]
      temp = command[(index+1):]
      index2 = temp.find(')')
      centre = temp[:index2]
      right = temp[(index2+1):]
      centreresult = parse(centre, outputString)
      if left and (left[-1].isnumeric() or left[-1] == ')'):
          left = left + '*'
      result = parse(left + str(centreresult) + right, outputString)
      print(result)
      return result
    if '+' in command or '-' in command:
        index = max(command.rfind('+'), command.rfind('-'))
        left = parse(command[:index], outputString)
        right = parse(command[(index+1):], outputString)
        if command[index] == "+":
            result = left + right
            outputString[0] = outputString[0] + (str(round(left, 2)) + '+' + str(round(right,2)) + "=" + str(round(result,2))) + '\n'
            return result
        else:
            result = left - right
            outputString[0] = outputString[0] + (str(round(left, 2)) + '-' + str(round(right,2)) + "=" + str(round(result,2))) + '\n'
            return result
    if '*' in command or '/' in command:
        index = max(command.rfind('*'), command.rfind('/'))
        left = parse(command[:index], outputString)
        right = parse(command[(index+1):], outputString)
        if command[index] == "*":
            result = left * right
            outputString[0] = outputString[0] + (str(round(left, 2))+'*'+str(round(right,2))+"="+str(round(result,2))) + '\n'
            return result
        else:
            result = left / right
            outputString[0] = outputString[0] + (str(round(left, 2)) + '/' + str(round(right,2)) + "=" + str(round(result,2))) + '\n'
            return result
    if 'adv' in command:
      index = command.find('adv')
      if command[:index] == "":
        left = 2
      else:
        left = parse(command[:index], outputString)
      right = parse(command[(index + 3):], outputString)
      result = 0
      printout = "Rolling "+str(left)+"d"+str(right)+" with advantage\n>"
      for x in range(left):
          num = random.randint(1, right)
          result = max(num, result)
          printout += ("  " + str(num))
      printout += ("\nMax = " + str(result))
      outputString[0] = outputString[0] + (printout) + '\n'
      return result
    if 'dis' in command:
      index = command.find('dis')
      if command[:index] == "":
        left = 2
      else:
        left = parse(command[:index], outputString)
      right = parse(command[(index + 3):], outputString)
      result = right
      printout = "Rolling "+str(left)+"d"+str(right)+" with disadvantage\n>"
      for x in range(left):
          num = random.randint(1, right)
          result = min(num, result)
          printout += ("  " + str(num))
      printout += ("\nMin = " + str(result))
      outputString[0] = outputString[0] + (printout) + '\n'
      return result
    if 'd' in command:
        index = command.find('d')
        if command[:index] == "":
          left = 1
        else:
          left = parse(command[:index], outputString)
        right = parse(command[(index + 1):], outputString)
        result = 0
        printout = "Rolling "+str(left)+"d"+str(right)+"\n>"
        for x in range(left):
            num = random.randint(1, right)
            result += num
            printout += ("  " + str(num))
        printout += ("\nTotal = " + str(result))
        outputString[0] = outputString[0] + (printout) + '\n'
        print('done roll')
        return result
    else:
        raise Exception("Parsing Error, check your input")

async def confirm_big_command(ctx, provided_token):
    global confirmation_token, pending_command
    # Ok, let's check the token first
    print("Command '"+pending_command+"' expecting token",confirmation_token+", got",provided_token)
    if confirmation_token != provided_token:
        await ctx.send("*Invalid token, cancelling command*")
        confirmation_token = pending_command = ""
        return
    if "remove_all_member_roles" in pending_command.strip():
        # get the proper role
        m_role = discord.utils.find(lambda r: r.name == MEMBER_ROLE, ctx.guild.roles)
        if not m_role:
            await ctx.send("*Error looking up role type:* `"+MEMBER_ROLE+"`")
            confirmation_token = pending_command = ""
            return
        print("Got member role I think, purging all instances from members")
        count = 0
        for member in m_role.members:
            count += 1
            await member.remove_roles(m_role, reason="Member role global removal (initiated by "+ctx.author.name+")")
        await ctx.send("<@&"+str(m_role.id)+"> *role removed from "+str(count)+" members.*\n*(See audit log for details)*")
    elif "kick_all_non_members" in pending_command.strip():
        # careful with this one! let's kick everyone who DOESN'T have the role.
        m_role = discord.utils.find(lambda r: r.name == MEMBER_ROLE, ctx.guild.roles)
        count = 0
        for member in ctx.guild.members:
            good_to_kick = True
            if member.bot:
            	good_to_kick=False
            for role in member.roles:
                if role==m_role or role.name in safe_roles:
                    good_to_kick = False
                    await ctx.send(member.name+" spared (has `"+role.name+"` role)")
                    break
            if good_to_kick:
                # this one gets the boot
                await ctx.send("Would kick "+member.name)
                #await message.guild.kick(member,reason="Global non-member removal (initiated by "+message.author.name+")")
                count += 1
        confirmation_token = pending_command = ""
        await ctx.send("*would have kicked "+str(count)+" non-members (See audit log for details)*")


@bot.command()
async def test_command(ctx):
    await ctx.send("Command works")

@bot.command()
async def zalgofy(ctx, *, arg):
    await ctx.send(zalgo.zalgo().zalgofy(arg))

# Upload a recoloured Gamers logo
@bot.command()
async def logo(ctx, *args):
    instructions = "*Usage:* "
    instructions += "`/logo [background] [tower] [dice] [pips]`"
    instructions += " | `/logo random`\n"
    instructions += "*Example:* `/logo 9f3036 ffffff dca948 ffffff`"

    if len(args) == 0 or args[0] == "random":
    # random recolour
        logo = discord.File(gamers_logo_change.random_recolour())
        await ctx.send(file=logo)
    elif len(args) == 4:
        # parse hex
        for arg in args:
            if re.match("[0-9A-Fa-f]{6}", arg) is None:
                await ctx.send(instructions)
                return
        logo = discord.File(gamers_logo_change.colour_logo(args[0], args[1], args[2], args[3]))
        await ctx.send(file=logo)
    else:
        await ctx.send(instructions)

@bot.command(aliases=['r'])
async def roll(ctx, *, arg):
    command = arg.lower().replace(" ","")
    if command.isnumeric():
        result = random.randint(1, int(command))
        await ctx.send('Rolling 1d' + command +':\n> ' + str(result))
        return
    outputString = [""]
    result = None
    try:
        result = parse(command, outputString)
        #await ctx.send(outputString[0] + 'Result = ' + str(round(result,2)))
        #print(bits, result)
    except:
        await ctx.send("Parsing error, please check your input")

    if result:
    	bits = outputString[0].split("\n")
    	await bot.send_embed(ctx, author_url=ctx.message.jump_url, author=ctx.author.display_name+bits[0].replace("Rolling"," rolled"), author_icon=ctx.author.display_avatar, title=bits[2].replace(" = ", ": "), description=bits[1].replace("> ", ""))

@bot.command()
@commands.check(verify_admin)
#@is_in_guild(GAMERS_GUILD_ID)
async def remove_all_member_roles(ctx):
    global confirmation_token, pending_command

    message = ctx.message
    msg = message.content
    print("Command:",msg)
    if message.guild.name not in advanced_guilds:
        print("Wrong guild ("+message.guild.name+")")
        return
    if await verify_admin(message): # Check the author is an admin for this one
        token = random.randint(1000,9999)
        response_msg = ":warning: *This will remove server access to all users with the* `"+MEMBER_ROLE+"` *role.* :warning:\n"
        response_msg += "***Are you sure you want to do this?***"
        response_msg += "\n*To confirm, type* `+confirm "+str(token)+"`"
        response_msg += "\n*To cancel, type* `+cancel`"
        confirmation_token = str(token)
        pending_command = msg
        await ctx.send(response_msg)

@bot.command()
@commands.check(verify_admin)
#@is_in_guild(GAMERS_GUILD_ID)
async def kick_all_non_members(ctx):
    global confirmation_token, pending_command
    print("called kick all non members")
    message = ctx.message
    msg = message.content
    token = random.randint(1000,9999)
    response_msg = ":warning: *This will kick all regular users without the* `"+MEMBER_ROLE+"` *role.* :warning:\n"
    response_msg += "*Committee, Ambassadors etc will not be affected.*"
    response_msg += "\n***Are you sure you want to do this?***"
    response_msg += "\n*To confirm, type* `+confirm "+str(token)+"`"
    response_msg += "\n*To cancel, type* `+cancel`"
    confirmation_token = str(token)
    pending_command = msg
    await ctx.send(response_msg)


@bot.command(name="validate")
@commands.check(verify_admin)
#@is_in_guild(GAMERS_GUILD_ID)
async def validate_membership(ctx, arg):

    # First get the username - check that's all working
    user = arg.strip()
    if "<@" not in user and ">" not in user:
        return
    userid = user.replace("<@", "").replace(">","")
    if not userid.isnumeric():
        return
    print("Validating", userid)
    member = ctx.guild.get_member(int(userid))
    if member == None or member not in ctx.guild.members:
        await ctx.send("*User not found*")
        return
    # now get the proper role
    m_role = discord.utils.get(ctx.guild.roles, name=MEMBER_ROLE)
    if m_role in member.roles:
        await ctx.send("*Already a member!*")
        return
    await member.add_roles(m_role)
    name = member.nick if member.nick != None else member.name
    await ctx.send("*"+name+" membership validated. Welcome!*")

@bot.command(name="confirm")
@commands.check(verify_admin)
#@is_in_guild(GAMERS_GUILD_ID)
async def confirm_dangerous_command(ctx, token):
    #check the token
    global confirmation_token, pending_command

    if confirmation_token == "" or pending_command == "":
        await ctx.send("*No pending actions to confirm*")
    else:
        await confirm_big_command(ctx, token)

@bot.command(name="cancel")
@commands.check(verify_admin)
#@is_in_guild(GAMERS_GUILD_ID)
async def cancel_dangerous_command(ctx):
    global confirmation_token, pending_command
    if confirmation_token == "" or pending_command == "":
        await ctx.send("*No actions pending*")
    else:
        await ctx.send("*Action* `"+pending_command+"` *cancelled.*")
        pending_command = confirmation_token = ""


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    #await client.change_presence(activity=discord.Game("with Dice"))

    if message.author == bot.user:
        return
    
    if not message.guild:
        # Relay message to master-bot-commands
        channel = await bot.bot_channel()
        member = channel.guild.get_member(message.author.id)
        msg = message.content
        #reply = "Message from "+message.author.display_name+":\n> "+msg.replace("\n", "\n> ")
        username = member.name+"#"+member.discriminator
        icon = member.display_avatar
        
        await bot.send_embed(channel, title="Message from "+member.display_name+" ("+username+")",\
        		 description=msg, thumbnail=icon)
        #await channel.send(reply)
        return

    msg = message.content.lower()
    chn = message.channel

    if "who\'s a good bot" in msg:
        await chn.send(zalgo.zalgo().zalgofy("Bunko is!"))

    elif "i would die for bunko" in msg or "i would die for you bunko" in msg:
        await chn.send(zalgo.zalgo().zalgofy("then perish"))
        await chn.send("||jk ily2 :heart:||")

    elif msg.strip() in ["i love you bunko", "i love bunko", "ily bunko"]:
        await chn.send(":heart:")

print("Starting up...")
bot.run(os.getenv('DISCORD_TOKEN'))
#guild = client.guilds[0]
#print("Connected to", guild.name)
print("Exiting")
