#!/usr/bin/env python3

import discord
import os
import random
from zalgo_text import zalgo
from dotenv import load_dotenv

# Bunko source code
# Discord bot for DU Gamers
# Original code by Maghnus (Ferrus), adapted by Adam (Pizza, github: rathdrummer) 


# Load environment variables, to keep Discord bot token distinct from this file
load_dotenv()

client = discord.Client()

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
    
    if "who\'s a good bot?" in msg:
        await chn.send(zalgo.zalgo().zalgofy("Bunko is!"))

    if msg.startswith('/r ') or msg.startswith('/roll'):
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
        