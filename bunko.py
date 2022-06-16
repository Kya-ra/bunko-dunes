#!/usr/bin/env python3

import discord
import os
import random
from zalgo_text import zalgo
from dotenv import load_dotenv

import gamers_logo_change

# Bunko source code
# Discord bot for DU Gamers
# Original code by Maghnus (Ferrus), adapted by Adam (Pizza, github: rathdrummer) 


# Load environment variables, to keep Discord bot token distinct from this file
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

async def roll(num):
    return random.randint(1, num)

async def parse (command, outputString):
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
      centreresult = await parse(centre, outputString)
      if left and (left[-1].isnumeric() or left[-1] == ')'):
          left = left + '*'
      result = await parse(left + str(centreresult) + right, outputString)
      print(result)
      return result
    if '+' in command or '-' in command:
        index = max(command.rfind('+'), command.rfind('-'))
        left = await parse(command[:index], outputString)
        right = await parse(command[(index+1):], outputString)
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
        left = await parse(command[:index], outputString)
        right = await parse(command[(index+1):], outputString)
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
        left = await parse(command[:index], outputString)
      right = await parse(command[(index + 3):], outputString)
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
        left = await parse(command[:index], outputString)
      right = await parse(command[(index + 3):], outputString)
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
          left = await parse(command[:index], outputString)
        right = await parse(command[(index + 1):], outputString)
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


@client.event
async def on_message(message):

    #await client.change_presence(activity=discord.Game("with Dice"))

    if message.author == client.user:
        return

    msg = message.content.lower()
    chn = message.channel        
    
    if "who\'s a good bot?" in msg or "who\'s a good bot!" in msg:
        await chn.send(zalgo.zalgo().zalgofy("Bunko is!"))

    if "i would die for bunko" in msg or "i would die for you bunko" in msg:
        await chn.send(zalgo.zalgo().zalgofy("then perish"))
        await chn.send("||jk ily2 :heart:||")

    if msg.startswith('/r ') or msg.startswith('/roll'):
        print("Rolling in",chn.name)
        command = msg[(msg.find(' ')+1):].lower().replace(" ","")
        if command.isnumeric():
          result = await roll(int(command))
          await chn.send('Rolling 1d' + int(command) +'\nResult = ' + str(result))
          return
        try:
          print(command)
          outputString = [""]
          result = await parse(command, outputString)
          await chn.send(outputString[0] + 'Result = ' + str(round(result,2)))
        except:
          await chn.send("Parsing error, please check your input")
    
    if msg.startswith('/logo'):
      print("Logo request in",chn.name)
      # Upload a recoloured Gamers logo
      # More functionality to come! Right now it just uploads a random one
      failed = False
      if len(msg) > 5:
        if msg.split(" ")[1] == "random":
          # random recolour
          logo = discord.File(gamers_logo_change.random_recolour())
          await chn.send(file=logo)
        elif len(msg.split(" ")) == 5:
          # parse hex
          args = msg.split(" ")
          for arg in args[1:]:
            if re.match("[0-9A-Fa-f]{6}", arg) is None:
              failed = True
              break
          if not failed:
            logo = discord.File(gamers_logo_change.colour_logo(args[1], args[2], args[3], args[4]))
            await chn.send(file=logo)  

        else:
          failed = True
      else:
        failed = True

      if failed:
        # Instruction code
        return_str = "*Usage:* "
        return_str += "`/logo [background] [tower] [dice] [pips]`"
        return_str += " | `/logo random`\n"
        return_str += "*Example:* `/logo 9f3036 ffffff dca948 ffffff`"
        await chn.send(return_str)

print("Starting up...")
client.run(os.getenv('DISCORD_TOKEN'))
#guild = client.guilds[0]
#print("Connected to", guild.name)
print("Exiting")
