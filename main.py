import discord
import os
import requests
import json
import random as rand
from replit import db
from keepalive import keep_alive

client = discord.Client()

commands = {'/help': 'lists all commands', '/inspire': 'sends an inspirational quote', '/addresponse [response_to_be_added]': 'adds a response', '/delresponse [response_to_be_deleted]': 'deletes a response', '/listresponse': 'lists all responses', '/toggleresponse': 'allows user to set whether or not the bot responds to non-command messages'}
greetings = ['hi', 'hi everyone', 'kleptocracy', 'hello', 'sup', 'what\'s up', 'dn']

if("responding" not in db.keys()):
  db["responding"] = True

#generates a random quote
def getRandomQuote():
  response = requests.get('https://zenquotes.io/api/random')
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " \n-" + json_data[0]['a']
  return (quote)

#adds a response to the list of responses
def addResponse(responseGr):
  if 'responses' in db.keys():
    responses = db['responses']
    if responseGr in responses:
      return False
    else:
      responses.append(responseGr)
      db['responses'] = responses
      return True
  else: 
    db['responses'] = [responseGr]
    return True 

#deletes a response from the responses list
def deleteResponse(response):
  if 'responses' in db.keys():
    responses = db['responses']
    if(response in responses):
      responses.remove(response)
      db['responses'] = responses
      return True
    else:
      return False
  else: 
    db['responses'] = []
    return False


#message that indicates that the bot is logged in and ready to run.
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  msg = message.content
  #checks if the message was sent by the Bot or by a user.
  if (message.author == client.user or message.author.bot):
    return

  #if msg == '/hello':
    #await message.channel.send('Hey There!')
  
  #declare totalResponses
  totalResponses = []
  if 'responses' in db.keys():
    totalResponses += list(db['responses'])

  #checks if this is a command
  if msg.startswith('/'):
    #sends an inspirational quote
    if msg == '/inspire':
      await message.channel.send(getRandomQuote())
    #command for adding a response
    elif msg.startswith('/addresponse'):
      if(len(msg.split('/addresponse ', 1)) >= 2):
        newResponse = msg.split('/addresponse ', 1)[1]
        if addResponse(newResponse):
          await message.channel.send("New response \'" + newResponse + "\' has been succesfully added.")
        else:
          await message.channel.send("Error: \'" + newResponse + "\' was previously added already.")
      else:
        await message.channel.send("Error: No response given.")
    #command to delete a response
    elif msg.startswith('/delresponse'):
      response = msg.split('/delresponse ', 1)
      if(len(response) >= 2):
        if deleteResponse(response[1]):
          await message.channel.send("Response \'" + response[1] + "\' has been succesfully deleted.")
        else:
          await message.channel.send("Error: \'" + response[1] + "\' was not in the current list of responses.")
      else: 
        await message.channel.send("Error: No response given.")
    #command to list out all responses
    elif msg.startswith('/listresponses'):
      responsesStr = ""
      if 'responses' in db.keys() and len(totalResponses) > 0:
        responsesStr += "List of responses, There are " + str(len(totalResponses)) + " responses:\n{"
        for i in totalResponses:
          responsesStr += (i + ", ")
        responsesStr = responsesStr[0 : len(responsesStr) - 2]
        responsesStr += "}"  
      else:
        responsesStr += "There are no responses."
      await message.channel.send(responsesStr)
    #command to list out all commands
    elif msg.startswith('/help'):
      commandsString = "__**List of all commands:**__\n"
      for keys,values in commands.items():
        commandsString += ("**" + keys + "**: ")
        commandsString += (values + "\n")
      await message.channel.send(commandsString + "")
    #allows user to set whether the bot responds or not.
    elif msg == '/toggleresponse':
      db["responding"] = not db["responding"]
      await message.channel.send("Successfully set responding to " + str(db["responding"]))
    #send error msg if the command is invalid
    else:
      await message.channel.send("Error: \'" + msg + "\' is not a valid command. Type \'/help\' for a list of valid commands.")

  #checks for specific words in a user's message, and sends a response
  elif db["responding"] and any(word in msg for word in greetings):
    await message.channel.send(rand.choice(totalResponses))

keep_alive()
client.run(os.getenv('TOKEN'))
    