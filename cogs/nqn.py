import random
import traceback
import uuid
import os
try:
  import emoji
except ImportError:
  print("you need to install emoji to use this cog")
  print("\"pip install emoji==2.0.0\"")
  os._exit(1)
import discord
import re
from discord.ext import commands
import asyncio

nqn_emoji_name = "nqn-nqn" # Name of the emoji that will show up the nqn emoji
nqn_emoji_id = "723880109898427914" #replace your bot nqn emoji id

class nqn(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_message(self, message: discord.Message):
    if message.author.bot:
      return

    if message.guild is None:
      return

    try:
      content = emoji.emojize(message.content, language='alias')
      mdlink = re.compile(r'\[(.*?)\]\((http|https|button)://(.+?)\)', flags=re.IGNORECASE).findall(content)
      mview = discord.ui.View(timeout=1)
      edited = False
      if mdlink:
        for mddata in mdlink:
          if mddata[1].lower() == "button":
            try:
              if mddata[2].lower().startswith(("http://", "https://")):
                mview.add_item(discord.ui.Button(label=mddata[0], url=mddata[2]))
              else:
                mview.add_item(discord.ui.Button(label=mddata[0], url="https://" + mddata[2]))
              content = content.replace(f"[{mddata[0]}]({mddata[1]}://{mddata[2]})", "")
              edited = True
            except:
              pass
          elif mddata[1].lower() == "http":
            edited = True
          elif mddata[1].lower() == "https":
            edited = True

      cpemoji = {}
      cpe = re.compile(r'<a?:.+?:\d*>', flags=re.IGNORECASE).findall(content)
      cpe = list(set(cpe))
      if cpe:
        for cpe_data in cpe:
          while True:
            ruuid = uuid.uuid4().hex
            if ruuid not in cpemoji.keys():
              cpemoji[ruuid] = cpe_data
              break
          content = content.replace(cpe_data, f'<{ruuid}>')

      rdemoji = re.compile(r':(.+?):', flags=re.IGNORECASE).findall(content)
      if rdemoji:
        rdemoji = list(set(rdemoji))
        for data in rdemoji:
          realdata = data
          tid = None
          checkdata = data.split("~")
          if checkdata[-1].isdigit():
            tid = int(checkdata[-1])
            data = "".join(checkdata[:-1])
          if data != nqn_emoji_name:
            useremojilist = [e for i in message.author.mutual_guilds for e in i.emojis if
                             (e.name.lower() == data.lower() or e.name.lower() == realdata.lower()) and e.available]
          else:
            useremojilist = [self.bot.get_emoji(nqn_emoji_id)]
          if useremojilist:
            choice_emoji = random.choice(useremojilist)
            content = re.compile(f':{data}:', flags=re.IGNORECASE).sub(str(choice_emoji), content)
            edited = True
        pass

      if cpe:
        for ruuid, cpe_data in cpemoji.items():
          content = content.replace(f'<{ruuid}>', cpe_data)

      if edited:
        listembed = []
        if message.reference:
          replym = await message.channel.fetch_message(message.reference.message_id)
          try:
            nickname = replym.author.nick
          except:
            nickname = None
          try:
            server_avatar = replym.author.guild_avatar.url
          except:
            server_avatar = None
          embed = discord.Embed(description=f"**[Reply to:]({replym.jump_url})** {replym.content}",
                                timestamp=replym.created_at)
          embed.set_author(name=nickname or replym.author.name,
                           icon_url=server_avatar or replym.author.display_avatar.url, url=replym.jump_url)
          listembed.append(embed)
        if message.attachments:
          notimg = []
          for i in message.attachments:
            if "image" in i.content_type and len(listembed) < 9:
              embed = discord.Embed(description=f"**[{i.filename}]({i.url})**")
              embed.set_image(url=i.url)
              listembed.append(embed)
            else:
              notimg.append(f"**[{i.filename}]({i.url})**")
          if notimg:
            filejoin = '\n'.join(notimg)
            embed = discord.Embed(description=f"{filejoin}")
            listembed.append(embed)
        mainc = message.channel.type
        if mainc == discord.ChannelType.private_thread or mainc == discord.ChannelType.public_thread or mainc == discord.ChannelType.news_thread:
          thchannel = message.channel
          channel = message.channel.parent
        else:
          thchannel = None
          channel = message.channel
        listwebhook = await channel.webhooks()
        botwebhook = discord.utils.get(listwebhook, user=self.bot.user)
        if botwebhook is None:
          botwebhook = await channel.create_webhook(name=self.bot.user.name, reason="NQN")
        phere = channel.permissions_for(message.author).mention_everyone
        prole = [role for role in message.guild.roles if role.mentionable or message.guild.owner == message.author]
        alm = discord.AllowedMentions(everyone=phere, roles=prole, users=True)
        username = message.author.nick or message.author.name
        avatar = message.author.guild_avatar or message.author.display_avatar
        try:
          await message.delete()
        except:
          pass
        if thchannel is not None:
          await botwebhook.send(content=content, username=username, avatar_url=avatar.url, allowed_mentions=alm,
                                thread=thchannel, view=mview, embeds=listembed)
        else:
          await botwebhook.send(content=content, username=username, avatar_url=avatar.url, allowed_mentions=alm,
                                view=mview, embeds=listembed)
    except Exception:
      traceback.print_exc()


async def setup(bot):
  await bot.add_cog(nqn(bot))

#credit
#code by: The DT#2747 (542602170080428063)
#and if you want to fix it please Pull requests :>
#github link: https://github.com/thedtvn/nqn-python
