import asyncio
import discord
import os
import requests
import logging, coloredlogs
from dotenv import load_dotenv

def log_message(channel: str, user: str, content: str):
  endpoint = os.environ.get('LOG_ENDPOINT') or 'http://localhost:8000'
  secret = os.environ.get('LOG_SECRET') or 'DEFAULT_SECRET'
  data = {'channel': channel, 'user': user, 'content': content}
  headers = {'X-Preshared-Key': secret}
  r = requests.post(endpoint, json=data, headers=headers)
  r.raise_for_status()

load_dotenv()
class EchoBot(discord.Bot):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.logger = logging.getLogger(os.environ.get('BOT_NAME', 'Echo Bot'))
    coloredlogs.install(level=logging.DEBUG, logger=self.logger)

  async def on_ready(self):
    self.logger.info(f'Connected as {self.user}')

bot = EchoBot(intents=discord.Intents(messages=True))

def extract_id(text: str) -> int | None:
  try:
    return int(text.strip('<@').strip('>'))
  except ValueError:
    return None

@bot.event
async def on_message(message: discord.Message):
  if message.author == bot.user: return
  # bot should not impersonate others
  if message.author.bot: return
  if len(message.content) <= 0: return
  if len(message.mentions) <= 0: return
  content = message.content.split(' ', 1)
  if len(content) == 1 and content[0].startswith('<@'):
    return await message.channel.send('找我嗎？')
  # check if the first mention is actually the bot (this is for replying with mention)
  actual_id = extract_id(content[0])
  if not actual_id: return
  if actual_id and actual_id != bot.user.id: return
  if not message.author.bot: await message.delete()
  text = content[1]
  if message.reference and message.reference.resolved and isinstance(message.reference.resolved, discord.Message):
    await message.reference.resolved.reply(text, mention_author=False)
  else:
    await message.channel.send(text)
  
  # logging part
  if message.author.guild.id != int(os.environ.get('LOG_GUILD_ID')): return
  channel_name = ''
  channel = await bot.fetch_channel(message.channel.id)
  if channel is None: channel_name = str(message.channel.id)
  else: channel_name = channel.name
  bot.loop.create_task(asyncio.to_thread(log_message, channel_name, message.author.display_name, text))

@bot.slash_command(name='image', description='上傳圖片')
@discord.option("attachment", description="要上傳的檔案", required=True)
@discord.option("spoiler", description="隱藏內容", required=True, default=False)
async def upload_image(ctx: discord.ApplicationContext, attachment: discord.Attachment, spoiler: bool):
  await ctx.defer()
  file = await attachment.to_file(spoiler=spoiler)
  await ctx.respond('OK', ephemeral=True, delete_after=1)
  await (await bot.fetch_channel(ctx.channel_id)).send(file=file)

bot.run(os.environ.get('BOT_TOKEN'))
