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

ADMIN_ROLE="Admin"
MEMBER_ROLE="access"
MAX_DICE_PER_ROLL = 100

advanced_guilds = ["DU Gamers","pizzabotics test server"]
confirmation_token = ""
pending_command = ""
safe_roles = ["Committee", "Committee.", "Server Administration", "Guest", "Service bots", "Ambassador", "Admin"]

# Bunko source code
# Discord bot for DU Gamers

# THIS IS KEPT FOR POSTERITY - I tried to replace all of Maghnus' code for dice
# rolling with my own but it was taking too long. Gonna roll it back from the repo.


# Load environment variables, to keep Discord bot token distinct from this file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents, command_prefix="/")

async def verify_admin(msg):
    for role in [r.name for r in msg.author.roles]:
        if role == ADMIN_ROLE:
            return True
    await msg.channel.send("Sorry, admin only")
    return False

def roll_unit_dice(dice):
    # Rolls dice in format "2d20", "6d6" etc. Doesn't support any math
    if dice.count("d") == 1 and dice.replace("d","").replace(".","").replace("-","").isnumeric():
            # okay looking good, lets try it out.

        parts = dice.split("d")
        if parts[0] == "":
            count = 1
        else:
            count = int(parts[0])
        sides = int(parts[1])

        if count < 0 or sides < 1:
            raise Exception("Parsing error: `"+dice+"`")

        if count > MAX_DICE_PER_ROLL:
            raise Exception("Too many dice (max "+string(MAX_DICE_PER_ROLL)+")")

        rolls = []
        for i in range(count):
            rolls += random.randint(1,sides)]
        return rolls.sum()

    elif dice.replace(".","").replace("-","").isnumeric():
        return int(float(dice))
    else:
        raise Exception("Parse error: `"+dice+"`")

def nest_parentheses(input):
    print("Input:",input)
    input = input.replace("+", "PLUS")\
             .replace("-", "MINUS")\
             .replace("*", "MULTIPLY")\
             .replace("/", "DIVIDE")


    # replaces all brackets by square brackets
    # and adds commas and double quotes when needed
    input = input.replace("(", "[")\
                 .replace(")", "]")\
                 .replace("[","\",[\"")\
                 .replace("]", "],\"")\
                 .replace("]", "\"]")\
                 .replace(" ", "")

    input = input.replace("\"\"", "").replace("],]", "]]")

    input = "[\"" + input + "\"]"

    print("Nested:",input)
    # safely evaluates the resulting string
    return ast.literal_eval(input)


def traverse_and_eval(tree):
    if isinstance(tree, str):
        return evaluate(tree)
    elif isinstance(tree, list):
        all_strings = True
        # clean up tree - connect top-level strings together
        newtree = []
        current_string = ""
        print("traversing:",tree)
        for branch in tree:
            if isinstance(branch, str):
                current_string += branch
            else:
                all_strings = False
                if current_string != "":
                    newtree += [current_string]
                    current_string = ""
                newtree += [branch]
        if current_string != "":
            newtree += [current_string]

        if all_strings:
            print("returning evaluation of","".join(tree))
            return evaluate("".join(tree))

        else:
            if len(newtree) == 1:
                newtree = newtree[0]

            # Tree has been cleaned up, let's try again.
            finaltree = []
            for branch in newtree:
                if isinstance(branch, list):
                    finaltree += [traverse_and_eval(branch)]
                else:
                    finaltree += [branch]
            return traverse_and_eval(finaltree)


def evaluate(formula):
        # 2nd-lowest level from the bottom. Dice values and multipliers.
    if "MINUS" in formula:
        formula = formula.replace("MINUS", "PLUS-")
    print("evaluating",formula)
    plus = formula.split("PLUS")
    p_total=0
    for p in plus:
        multiply = p.split("MULTIPLY")
        m_total = 1
        for m in multiply:
            divide = m.split("DIVIDE")
            d_total = float(roll_unit_dice(divide[0]))
            if len(divide)>1:
                for d in divide[1:]:
                    d_total /= float(roll_unit_dice(d))
            m_total *= d_total
        p_total += m_total
    print("Result:",p_total)
    return str(p_total)


def parse(command):
    command = command.strip().replace(" ", "").replace(" ", "")
    if command.isnumeric():
        return int(command)
    elif any(char in command for char in ["+", "-", "*", "/", "dis", "adv", "(", ")"]):
        # okay lets do this, pemdas time

        cmd = [command.replace("+", "PLUS")\
                         .replace("-", "MINUS")\
                         .replace("*", "MULTIPLY")\
                         .replace("/", "DIVIDE")]

        # First, parentheses. Split those bad guys up.
        if any(char in command for char in ["(", ")"]):
            cmd = nest_parentheses(command)

        return traverse_and_eval(cmd)

    else:
        return roll_unit_dice(command)

async def confirm_big_command(message):
    global confirmation_token, pending_command
    # Ok, let's check the token first
    provided_token = message.content.strip().split(" ")[1]
    print("Command '"+pending_command+"' expecting token",confirmation_token+", got",provided_token)
    if confirmation_token != provided_token:
        await message.channel.send("*Invalid token, cancelling command*")
        confirmation_token = pending_command = ""
        return
    if pending_command.strip() == "/remove_all_member_roles":
        # get the proper role
        m_role = discord.utils.find(lambda r: r.name == MEMBER_ROLE, message.guild.roles)
        if not m_role:
            await message.channel.send("*Error looking up role type:* "+MEMBER_ROLE)
            confirmation_token = pending_command = ""
            return
        print("Got member role I think, purging all instances from members")
        count = 0
        for member in m_role.members:
            count += 1
            await member.remove_roles(m_role, reason="Member role global removal (initiated by "+message.author.name+")")
        await message.channel.send("<@&"+str(m_role.id)+"> *role removed from "+str(count)+" members.*\n*(See audit log for details)*")
    elif pending_command.strip() == "/kick_all_non_members":
        # careful with this one! let's kick everyone who DOESN'T have the role.
        m_role = discord.utils.find(lambda r: r.name == MEMBER_ROLE, message.guild.roles)
        count = 0
        for member in message.guild.members:
            good_to_kick = True
            for role in member.roles:
                if role==m_role or role.name in safe_roles:
                    good_to_kick = False
                    await message.channel.send(member.name+" spared (has `"+role.name+"` role)")
                    break
            if good_to_kick:
                # this one gets the boot
                await message.channel.send("Would kick "+member.name)
                #await message.guild.kick(member,reason="Global non-member removal (initiated by "+message.author.name+")")
                count += 1
        confirmation_token = pending_command = ""
        await message.channel.send("*would have kicked "+str(count)+" non-members (See audit log for details)*")


@bot.command()
async def test_command(ctx):
    await ctx.send("Command works")

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

@bot.command()
async def roll(ctx, *, arg):
    command = arg.lower().replace(" ","")
    if command.isnumeric():
        result = random.randint(1, command)
        await ctx.send('Rolling 1d' + int(command) +':\n> ' + str(result))
        return
    try:
        outputString = [""]
        result = parse(command, outputString)
        await ctx.send(outputString[0] + 'Result = ' + str(round(result,2)))
    except:
        await ctx.send("Parsing error, please check your input")

@bot.event
async def on_messages(message):
    await bot.process_commands()
    global confirmation_token, pending_command

    #await client.change_presence(activity=discord.Game("with Dice"))

    if message.author == bot.user:
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

    elif msg.startswith("/remove_all_member_roles"):
        print("Command:",msg)
        if message.guild.name not in advanced_guilds:
            print("Wrong guild ("+message.guild.name+")")
            return
        if await verify_admin(message): # Check the author is an admin for this one
            token = random.randint(1000,9999)
            response_msg = ":warning: *This will remove server access to all users with the* `"+MEMBER_ROLE+"` *role.* :warning:\n"
            response_msg += "***Are you sure you want to do this?***"
            response_msg += "\n*To confirm, type* `/confirm "+str(token)+"`"
            response_msg += "\n*To cancel, type* `/cancel`"
            confirmation_token = str(token)
            pending_command = msg
            await chn.send(response_msg)

    elif msg.startswith("/kick_all_non_members"):
        if message.guild.name not in advanced_guilds:
            print("Wrong guild (expecting DU Gamers, got",message.guild.name+")")
            return
        if message.guild.name == "DU Gamers" and await verify_admin(message):
            token = random.randint(1000,9999)
            response_msg = ":warning: *This will kick all regular users without the* `"+MEMBER_ROLE+"` *role.* :warning:\n"
            response_msg += "*Committee, Ambassadors etc will not be affected.*"
            response_msg += "\n***Are you sure you want to do this?***"
            response_msg += "\n*To confirm, type* `/confirm "+str(token)+"`"
            response_msg += "\n*To cancel, type* `/cancel`"
            confirmation_token = str(token)
            pending_command = msg
            await chn.send(response_msg)



    elif msg.startswith("/validate "):
        if await verify_admin(message):
            # First get the username - check that's all working
            user = msg.split("/validate ")[1]
            if "<@" not in user and ">" not in user:
                return
            userid = user.replace("<@", "").replace(">","")
            if not userid.isnumeric():
                return
            print("Validating", userid)
            member = message.guild.get_member(int(userid))
            if member == None or member not in message.guild.members:
                await chn.send("*User not found*")
                return
            # now get the proper role
            m_role = discord.utils.get(message.guild.roles, name=MEMBER_ROLE)
            if m_role in member.roles:
                await chn.send("*Already a member!*")
                return
            await member.add_roles(m_role)
            name = member.nick if member.nick != None else member.name
            await chn.send("*"+name+" membership validated. Welcome!*")

    elif msg.startswith("/confirm "):
        if await verify_admin(message):
            #check the token
            if confirmation_token == "" or pending_command == "":
                await chn.send("*No pending actions to confirm*")
            else:
                await confirm_big_command(message)

    elif msg.startswith("/cancel"):
        if await verify_admin(message):
            if confirmation_token == "" or pending_command == "":
                await chn.send("*No actions pending*")
            else:
                await chn.send("*Action* `"+pending_command+"` *cancelled.*")
                pending_command = confirmation_token = ""

print("Starting up...")
print(traverse_and_eval(nest_parentheses("2d6*(2-7)/3+8")))
bot.run(os.getenv('DISCORD_TOKEN'))
#guild = client.guilds[0]
#print("Connected to", guild.name)
print("Exiting")
