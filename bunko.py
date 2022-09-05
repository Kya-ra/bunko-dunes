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
from dice import parse
import member_validation
import bunko_tasks
import library

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
# Original code by Maghnus (Ferrus), heavily modified by Adam (Pizza, github: rathdrummer)


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

    async def send_embed(self, ctx, ref=None, author_url=None, url=None, title="DU Gamers", description="", color=0x9f3036, thumbnail=None, fieldname=None, fieldvalue="\u200b", author=None, author_icon=None, footer=None,view=None):
        e = discord.Embed(title=title, url=url, description=description, color=color)
        if author:
            e.set_author(name=author, icon_url=author_icon, url=author_url)
        if thumbnail:
            e.set_thumbnail(url=thumbnail)
        if footer:
            e.set_footer(text=footer)
        if fieldname:
            if fieldvalue:
                e.add_field(name=fieldname, value=fieldvalue)
            else:
                e.add_field(name=fieldname)
        if not view:
            await ctx.send(embed=e, reference=ref)
        else:
            await ctx.send(embed=e, view=view, reference=ref)
            
"""
class ValidateButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.member=None
        print("view created")
        
    @discord.ui.button(label="Grant access",style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("validated via button")
        await interaction.response.send_message('Granting access', ephemeral=True)
        m_role = discord.utils.get((await bot.gamers()).roles, name=MEMBER_ROLE)
        await self.member.add_roles(m_role)
        self.stop()
"""


# Load environment variables, to keep Discord bot token distinct from this file
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


@bot.command(aliases = ["you_good_bunko"])
async def test_command(ctx):
    await ctx.send("I'm g :)")

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
        await bot.send_embed(ctx, ref=ctx.message, author_url=ctx.message.jump_url, author=ctx.author.display_name+bits[0].replace("Rolling"," rolled"), author_icon=ctx.author.display_avatar, title=result, description=bits[1].replace("> ", ""))


@bot.command(aliases=["l", "search", "library"])
async def library_search(ctx, *, args):
    await ctx.typing()
    
    if library.is_library_id(args.upper()):
        # ID lookup

        args = args.upper()
        types={"R" : "Role-playing game",
                "W" : "Wargame",
                "C" : "Card game",
                "B" : "Board game"}
        
        result = library.get_entry(args)[0]
        
        if "|" in result["franchise"]:
            franchises = "\n".join(result["franchise"].split("|"))
        else: 
            franchises = result["franchise"]

        if "|" in result["other_images"]:
            otherpics = ""
            count = 1
            for p in result["other_images"].split("|"):
                otherpics += "[pic"+str(count)+"]("+p+") "
                count+=1
        else: 
            otherpics = "[pic]("+result["other_images"]+")"
        
        e = discord.Embed(title=result["name"],colour=0xdca948, description=franchises)

        e.set_author(name="Library item")
        e.add_field(name="Type",value=types[args[0]])
        
        if otherpics:
            e.add_field(name="Other images",value=otherpics)
            
        if result["main_image"]:
            e.set_thumbnail(url=result["main_image"])

        e.set_footer(text=args)
        
        await ctx.reply(embed=e)
        
    else:
        # search query
        result = library.query(args)
        outstring = "*" +args+ "*\n"+ library.make_query_string(result)
        await bot.send_embed(ctx, ref=ctx.message, color=0xdca948,title="Library search", description = outstring, footer="To view an item, search for its ID", )
            

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

@bot.command(name="?")
async def list_all_commands(ctx):
    message = "*Bunko 1.2* :robot::book::game_die::heart:\n\nHere's the stuff I can do right now:\n"
    message += "> **+roll** or **+r** - `+roll d20`, `+r 3dis6`\n" 
    message += "> **+library** or **+l** - `+l Monster Manual`\n"
    message += "> **+logo** - `+logo 990055 fff00f f55fff 000000`, `+logo random`\n"
    message += "> **+zalgofy** - `+zalgofy hello friends`" 
    await ctx.send(message)
    

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

@bot.command(aliases=["who_is_a_guest"])
@commands.check(verify_admin)
@is_in_guild(GAMERS_GUILD_ID)
async def list_current_guests(ctx):
    gamers = await bot.gamers()
    guestlist = ""
    count = 0
    for gamer in gamers.members:
        if "Guest" in [x.name for x in gamer.roles]:
            # got guest
            guestlist += "> " + gamer.display_name + " (" + gamer.name + "#" + gamer.discriminator + ")\n"
            count += 1
            
    message = str(count)+" current users with \"Guest\" role:\n" + guestlist
    await ctx.send(message)


@bot.command(aliases=["who_is_not_a_member"])
@commands.check(verify_admin)
@is_in_guild(GAMERS_GUILD_ID)
async def list_non_members(ctx):
    await ctx.typing()
    gamers = await bot.gamers()
    guestlist = "Non-members:\n```"
    count = 0
    members = 0
    for gamer in gamers.members:
        members += 1
        membership = False
        safe = False
        notes = ""
        for role in gamer.roles:
            if role.name in safe_roles and role.name != "Guest":
                safe = True
                #break
            if role.name == MEMBER_ROLE:
                membership = True
            if role.name == "Guest":
                notes = "(Guest)"
        if not membership and not safe:
            if len(guestlist) > 1500:
                await ctx.send(guestlist+"```")
                guestlist = "```"
                await ctx.typing()
            guestlist += gamer.display_name.ljust(20) + (gamer.name + "#" + gamer.discriminator).ljust(20) + notes+"\n"
            count += 1
            
    message = guestlist +"```"+ str(count)+" current non-member users (not including bots, Committee etc)"
    await ctx.send(message)

@bot.command()
@commands.check(verify_admin)
@is_in_guild(GAMERS_GUILD_ID)
async def debug_guest_removal(ctx):
    await bunko_tasks.remove_guests(ctx)

@bot.command()
@commands.check(verify_admin)
@is_in_guild(GAMERS_GUILD_ID)
async def admin_commands(ctx):
    message = "Here's my admin-only commands:\n\n"
    message += "> **+who_is_a_guest** or **+list_current_guests**\n" 
    message += "> **+who_is_not_a_member** or **+list_non_members**\n" 
    message += "\n"
    message += "High stakes commands (will send an 'Are you sure' message, requiring confirmation):\n"
    message += "> **+remove_all_member_roles** - removes the 'DU Gamers Member' role from everyone\n"
    message += "> **+kick_all_non_members** - kicks everyone that doesn't have the 'DU Gamers Member' role (barring bots, committee, etc)\n"
    message += "That last one is untested and could have serious consequences if it fails (i.e. kicking everyone) - maybe try not to use if possible!"
    await ctx.send(message)


@bot.event
async def on_message(message):
    await bot.process_commands(message)

    #await client.change_presence(activity=discord.Game("with Dice"))

    if message.author == bot.user:
        return

    if not message.guild:
        await on_dm(message)
        return

    msg = message.content.lower()
    chn = message.channel

    if (message.is_system() and message.type == discord.MessageType.new_member and message.guild.name in ["DU Gamers", "pizzabotics test server"]) or msg == "bunko welcome debug a-go-go":
        print("Welcome message for "+message.author.display_name)
        content="If you could just do a few things, we can grant you access to the rest of the server:\n\n"
        content+="1. Please say hi :grinning:\n\n"
        content+="2. Have a read of the <#755069071342436452>, and pick your pronouns in <#760455413148811285>\n\n"
        content+="3. Edit your nickname to include the name you go by in real life (click on the server name on the top right, then \"Edit Server Profile\")\n\n"
        content+="4. Send me (Bunko) your tcd.ie email address in a private Discord message, I'll check your membership, and <@&371350576350494730> will let you in!"
    
        await bot.send_embed(chn,ref=message, title="Welcome "+message.author.display_name+"!", description=content,color=0xdca948,\
             footer="Your email will stay confidential and only be used to check your membership; it won't ever be linked to your username.")

        return

    if "who\'s a good bot" in msg:
        await chn.send(zalgo.zalgo().zalgofy("Bunko is!"))

    elif "i would die for bunko" in msg or "i would die for you bunko" in msg:
        await chn.send(zalgo.zalgo().zalgofy("then perish"))
        await chn.send("||jk ily2 :heart:||")

    elif msg.strip() in ["i love you bunko", "i love bunko", "ily bunko"]:
        await chn.send(":heart:")

async def on_dm(message):

    if member_validation.valid_email(message.content.strip()):
        # Got an email, this could be someone trying to verify their account. 
        # First check they are in the Gamers server.
        user = message.author

        if user in (await bot.gamers()).members:
            # gottem, let's run through the validation process
            member = (await bot.gamers()).get_member(user.id)
            await message.channel.typing()
            returncode = member_validation.check_membership(message.content.strip())

            if returncode["status"]:
                # Verified and validated. First let Committee know.
                username = member.name+"#"+member.discriminator
                
                let_in ="Once they've introduced themselves, click below to let them in"
                committee_msg = "Membership confirmed"
                desc = let_in
                member_response = "Committee has been notified and will grant you access soon."

                if "already" in returncode["details"]:
                    committee_msg = "Membership already confirmed"
                    member_response = "If you still don't have access, reply to this DM and your message will be forwarded to Committee."
                if "added" in returncode["details"]:
                    pass
                else:
                    desc += "\nReturn code: `"+returncode["details"]+"`"

                # try to make a button
                committee_channel = await bot.bot_channel()
                icon = member.display_avatar
 
                view=discord.ui.View()
                buttonSign = discord.ui.Button(label="Grant access to "+member.display_name, style=discord.ButtonStyle.green)

                async def buttonSign_callback(interaction):
                    print("validated via button")
                    await interaction.response.send_message('Granting access', ephemeral=True)
                    m_role = discord.utils.get((await bot.gamers()).roles, name=MEMBER_ROLE)
                    await member.add_roles(m_role)

                buttonSign.callback=buttonSign_callback
                view.add_item(item=buttonSign)

                
                await bot.send_embed(committee_channel, author=member.display_name+" ("+username+")",  title=committee_msg,\
                             description=desc, thumbnail=icon, color=0xdca948, view=view)

                await bot.send_embed(message.channel, title=committee_msg+"!",description=member_response, color=0xdca948)
                
            else:
                # User does not have an account, let them know

                await bot.send_embed(message.channel, title="Can't seem to find your DU Gamers membership",\
                            description="Make sure you signed up to the society at https://trinitysocietieshub.com/ "\
                            +"and that you gave the right email (your @tcd.ie email).\n\n"\
                            +"If you're sure you're a member, let us know - reply to this DM, and your message will be sent on to Committee.")

                committee_channel = await bot.bot_channel()
                await committee_channel.send("*Couldn't find membership for "+member.display_name+" ("+member.name+"#"+member.discriminator+")*")            
            
        else:
            await relay_message_to_committee(message)

    else:
        await relay_message_to_committee(message)

"""
# welcome message
@bot.event
async def on_member_join(member):
    intro_channel = discord.utils.get(member.guild.channels, name="introductions")
"""    

async def relay_message_to_committee(message):
     # Relay message to master-bot-commands
    channel = await bot.bot_channel()
    member = channel.guild.get_member(message.author.id)
    msg = message.content
    username = member.name+"#"+member.discriminator
    icon = member.display_avatar
    
    await bot.send_embed(channel, title="Message from "+member.display_name+" ("+username+")",\
             description=msg, thumbnail=icon)

@bot.event
async def on_ready():
    #connect up all the shit
    await bot.wait_until_ready()
    print("Logged in to guilds",[g.name for g in bot.guilds])
    bc = await bot.bot_channel()
    bunko_tasks.remove_guests.start(bc)


print("Starting up...")
bot.run(os.getenv('DISCORD_TOKEN'))
Bunko
#guild = client.guilds[0]
#print("Connected to", guild.name)
print("Exiting")
