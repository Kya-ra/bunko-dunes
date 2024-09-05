#!/usr/bin/env python3

import discord
import requests
from discord.ext import commands
import os
import re
import random
from zalgo_text import zalgo
from dotenv import load_dotenv

import member_validation
#import bunko_tasks

ADMIN_ROLE="Discord Administrator"
MEMBER_ROLE="DUNeS Member"

DUNES_SERVER_ID=855920166986186783
SECRET_BOT_CHANNEL_ID=855920167431438345

advanced_guilds = ["DUNeS - DU Neurodiversity Society","neurotests"]
confirmation_token = ""
pending_command = ""
safe_roles = ["Committee", "Executive.", "Discord Administrator", "Server Guest", "Bot", "Alumni"]

# Bunko source code
# Discord bot for DU Gamers
# Original code by Maghnus (Ferrus), heavily modified by Adam (Pizza, github: rathdrummer)
# Adaptation for DUNeS by Kyara and Ash


class Bunko(commands.Bot):
    gamers_guild = None
    gamers_bot_channel = None

    async def gamers(self):
        if self.gamers_guild == None:
            self.gamers_guild = self.get_guild(DUNES_SERVER_ID)
        return self.gamers_guild

    async def bot_channel(self):
        g = await self.gamers()
        return await g.fetch_channel(SECRET_BOT_CHANNEL_ID)

    async def send_embed(self, ctx, ref=None, author_url=None, url=None, title="DUNeS", description="", color=0x9f3036, thumbnail=None, fieldname=None, fieldvalue="\u200b", author=None, author_icon=None, footer=None,view=None):
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


@bot.command(aliases = ["you_good_bunko", "you_ok_bunko", "you_g_bunko"])
async def test_command(ctx):
    await ctx.send("I'm g :)")

@bot.command()
async def zalgofy(ctx, *, arg):
    await ctx.send(zalgo.zalgo().zalgofy(arg))

@bot.command()
@commands.check(verify_admin)
#@is_in_guild(DUNES_SERVER_ID)
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
#@is_in_guild(DUNES_SERVER_ID)
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
#@is_in_guild(DUNES_SERVER_ID)
async def validate_membership(ctx,*, arg):

    # First get the username - check that's all working
    user = arg.strip()
    member = None
    
    if "<@" in user and ">" in user:
        #tag given
        print("got tagged validation command")
        
        userid = user.replace("<@", "").replace(">","")
        
        if not userid.isnumeric():
            await ctx.reply("*Format: `username#1234`*")
            return
                           
        member = ctx.guild.get_member(int(userid))
        
    else:
        #plaintext given
        print("got plaintext validation command")
        if user.count("#") == 1:
            [name, discriminator] = user.split("#")
            print(name)
            print(discriminator)

            
            for m in ctx.guild.members:
                if m.name.lower().strip() == name.lower().strip() and str(m.discriminator) == discriminator:
                    member = m
                    break
                    
            if not member:
                await ctx.reply("*User not found*")
                return
                
        else:
            await ctx.reply("*Format: `username#1234`*")
            return
        
    
    if member == None or member not in ctx.guild.members:
        await ctx.send("*User not found*")
        return
        
    # now get the proper role
    m_role = discord.utils.get(ctx.guild.roles, name=MEMBER_ROLE)
    
    if m_role in member.roles:
        await ctx.reply("*Already a member :white_check_mark:*")
        return
        
    await member.add_roles(m_role)
    name = member.nick if member.nick != None else member.name
    await ctx.send("*"+name+" membership validated. Welcome!*")

@bot.command(name="confirm")
@commands.check(verify_admin)
#@is_in_guild(DUNES_SERVER_ID)
async def confirm_dangerous_command(ctx, token):
    #check the token
    global confirmation_token, pending_command

    if confirmation_token == "" or pending_command == "":
        await ctx.send("*No pending actions to confirm*")
    else:
        await confirm_big_command(ctx, token)

@bot.command(name="cancel")
@commands.check(verify_admin)
#@is_in_guild(DUNES_SERVER_ID)
async def cancel_dangerous_command(ctx):
    global confirmation_token, pending_command
    if confirmation_token == "" or pending_command == "":
        await ctx.send("*No actions pending*")
    else:
        await ctx.send("*Action* `"+pending_command+"` *cancelled.*")
        pending_command = confirmation_token = ""

@bot.command(aliases=["who_is_a_guest"])
@commands.check(verify_admin)
@is_in_guild(DUNES_SERVER_ID)
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
@is_in_guild(DUNES_SERVER_ID)
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
@is_in_guild(DUNES_SERVER_ID)
async def debug_guest_removal(ctx):
    await bunko_tasks.remove_guests(ctx)

@bot.command()
@commands.check(verify_admin)
@is_in_guild(DUNES_SERVER_ID)
async def admin_commands(ctx):
    message = "Here's my admin-only commands:\n\n"
    message += "> **+who_is_a_guest** or **+list_current_guests**\n" 
    message += "> **+who_is_not_a_member** or **+list_non_members**\n"
    message += "\n"
    message += "High stakes commands (will send an 'Are you sure' message, requiring confirmation):\n"
    message += "> **+remove_all_member_roles** - removes the 'DU Gamers Member' role from everyone\n"
    message += "> **+kick_all_non_members** - kicks everyone that doesn't have the 'DUNeS Member' role (barring bots, committee, etc)\n"
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

    if (message.is_system() and message.type == discord.MessageType.new_member and message.guild.name in advanced_guilds) or msg == "bunko welcome debug a-go-go" or (msg == ".signup" and message.guild.name in advanced_guilds):
        print("Welcome message for "+message.author.display_name)
        content="If you could just do a few things, we can grant you access to the rest of the server:\n\n"
        content+="1. Have a read of the <#1206320208344514640>, and pick your roles in <#855920167632896047>\n\n"
        content+="2. Send me (Neurobot) your tcd.ie email address in a private Discord message, I'll check your membership, and then let you in!\n\n"
        content+="And just remember, this won't work if you haven't signed up on [trinitysocietieshub.com](https://trinitysocietieshub.com/collections/social/products/neurodiversity)!"
    
        await bot.send_embed(chn,ref=message, title="Welcome "+message.author.display_name+"!", description=content,color=0xdca948,
             footer="Your email will stay confidential and only be used to check your membership; it won't ever be linked to your username.")

        return

    if "who\'s a good bot" in msg:
        await chn.send(zalgo.zalgo().zalgofy("Obviously not Soup!"))

    elif "bunko" in msg:
        await chn.send("I have no idea who that is.")
        await chn.send("||jk i'll always remember where i came from :D :heart:||")

    elif msg.strip() in ["metho", "who's metho", "whos metho", "hi metho"]:
        await chn.send("https://tenor.com/bRUYj.gif")

    elif msg.strip() in ["who is the best committee member", "whos the best committee member"]:
        await chn.send("Obviously Soup!")

async def on_dm(message):

    if "@" in message.content:
        # Filter out email information, pass to validation thingy, and forward filtered message to committee
        match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', message.content)

        email = ""
        
        
        if match:
            email=match.group(0)
            message.content = message.content.replace(email, "`[EMAIL]`")

            forward = True
            
            if member_validation.valid_email(message.content.strip()):
                #only thing in the message is email. dont' bother forwarding the rest
                forward = False
                
            # Got an email, this could be someone trying to verify their account. 
            # First check they are in the Gamers server.
            user = message.author

            if user in (await bot.gamers()).members:
                # gottem, let's run through the validation process
                member = (await bot.gamers()).get_member(user.id)
                await message.channel.typing()
                returncode = member_validation.check_membership(email.lower())
                

                if returncode["status"]:
                    # Verified and validated. First let Committee know.
                    username = member.name

                    await bot.send_embed(message.channel, title="Membership confirmed", description=" You should be granted access soon!")
                    m_role = discord.utils.get((await bot.gamers()).roles, name=MEMBER_ROLE)
                    await member.add_roles(m_role)

                    if "already" in returncode["details"]:
                        await bot.send_embed(message.channel, title="Membership already confirmed", description="If you still don't have access, reply to this DM and your message will be forwarded to Committee.")
                    if "added" in returncode["details"]:
                        pass
                    else:
                        desc += "\nReturn code: `"+returncode["details"]+"`"
                    
                else:
                    # User does not have an account, let them know

                    await bot.send_embed(message.channel, title="Can't seem to find your DUNeS membership",
                                description="Make sure you signed up to the society at https://trinitysocietieshub.com/ "\
                                +"and that you gave the right email (your @tcd.ie email).\n\n"\
                                +"If you've signed up within the past hour or so, give it another hour and try again. CSC data can be slow to update on our end.\n\n"\
                                +"If it still isn't working and you're sure you're a member, let us know - reply to this DM, and your message will be sent on to Committee.")

                    committee_channel = await bot.bot_channel()
                    await committee_channel.send("*Couldn't find membership for "+member.display_name+" ("+member.name+")*")            

                if forward:
                    await relay_message_to_committee(message)
              
            else:
                await relay_message_to_committee(message)

    else:
        await relay_message_to_committee(message)


# welcome message
@bot.event
async def on_member_join(member):
    intro_channel = discord.utils.get(member.guild.channels, name="introductions")


async def relay_message_to_committee(message):
    # Relay message to master-bot-commands
    channel = await bot.bot_channel()
    member = (await bot.gamers()).get_member(message.author.id)
    if not member:
        member = message.author
    msg = message.content
    username = member.name
    icon = member.display_avatar
    
    await bot.send_embed(channel, title="Message from "+member.display_name+" ("+username+")",
             description=msg, thumbnail=icon)

@bot.event
async def on_ready():
    #connect up all the shit
    await bot.wait_until_ready()
    print("Logged in to guilds",[g.name for g in bot.guilds])
    bc = await bot.bot_channel()
    #bunko_tasks.remove_guests.start(bc)


print("Starting up...")
bot.run(os.getenv('DISCORD_TOKEN')) #DO NOT PUT THIS IN LIVE CODE
guild = client.guilds[0]
print("Connected to", guild.name)
print("Exiting")
