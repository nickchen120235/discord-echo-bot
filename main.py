import discord
import os
import logging, coloredlogs
from dotenv import load_dotenv

load_dotenv()
class EchoBot(discord.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.logger = logging.getLogger(os.environ.get('BOT_NAME', 'Echo Bot'))
    coloredlogs.install(level=logging.DEBUG, logger=self.logger)

  async def on_ready(self):
    self.logger.info(f'Connected as {self.user}')

bot = EchoBot(intents=discord.Intents(messages=True))

@bot.event
async def on_message(message: discord.Message):
  if message.author == bot.user: return
  if len(message.content) < 0: return
  text = message.content.split(' ', 1)[1]
  await message.delete()
  if message.reference and message.reference.resolved and isinstance(message.reference.resolved, discord.Message):
    await message.reference.resolved.reply(text, mention_author=False)
  else:
    await message.channel.send(text)

bot.run(os.environ.get('BOT_TOKEN'))
