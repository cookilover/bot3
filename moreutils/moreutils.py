﻿# -*- coding: utf-8 -*-
import colorsys
import datetime
import os
import random
import re

import discord
import matplotlib.colors as colors
from discord.ext import commands

from cogs.utils import chat_formatting as chat
from cogs.utils.dataIO import dataIO


def hex_to_rgb(hex_string):
    rgb = colors.hex2color(hex_string)
    return tuple([int(255 * x) for x in rgb])


def get_int_from_rgb(rgb):
    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]
    rgb_int = (red << 16) + (green << 8) + blue
    return rgb_int


def rgb_to_cmyk(r, g, b):
    rgb_scale = 255
    cmyk_scale = 100
    if (r == 0) and (g == 0) and (b == 0):
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / float(rgb_scale)
    m = 1 - g / float(rgb_scale)
    y = 1 - b / float(rgb_scale)

    # extract out k [0,1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy)
    m = (m - min_cmy)
    y = (y - min_cmy)
    k = min_cmy

    # rescale to the range [0,cmyk_scale]
    return c * cmyk_scale, m * cmyk_scale, y * cmyk_scale, k * cmyk_scale


def bool_emojify(bool_var: bool) -> str:
    return "✔" if bool_var else "❌"


class CustomChecks:
    # noinspection PyMethodParameters
    def selfbot():
        def predicate(ctx):
            if ctx.bot.user.bot:  # if bot.user.bot is True - bot is not selfbot
                return False
            return True

        return commands.check(predicate)


class MoreUtils:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_file = "data/moreutils/config.json"
        self.config = dataIO.load_json(self.config_file)

    @commands.group(pass_context=True)
    @CustomChecks.selfbot()
    async def utilsset(self, ctx):
        """More utils settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @utilsset.group(pass_context=True)
    @CustomChecks.selfbot()
    async def signature(self, ctx):
        """Signature settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @signature.command()
    @CustomChecks.selfbot()
    async def title(self, *, title: str):
        """Set signature title"""
        self.config["signature_title"] = title
        dataIO.save_json(self.config_file, self.config)
        await self.bot.say(chat.info("Signature title changed to {}".format(title)))

    @signature.command(aliases=["desc"])
    @CustomChecks.selfbot()
    async def description(self, *, description: str):
        """Set signature description"""
        self.config["signature_desc"] = description
        dataIO.save_json(self.config_file, self.config)
        await self.bot.say(chat.info("Signature description changed to {}".format(description)))

    @signature.command()
    @CustomChecks.selfbot()
    async def url(self, *, url: str):
        """Set signature title"""
        self.config["signature_url"] = url
        dataIO.save_json(self.config_file, self.config)
        await self.bot.say(chat.info("Signature url changed to {}".format(url)))

    @signature.command()
    @CustomChecks.selfbot()
    async def field_name(self, *, field_name: str):
        """Set signature field name"""
        self.config["signature_field_name"] = field_name
        dataIO.save_json(self.config_file, self.config)
        await self.bot.say(chat.info("Signature field name changed to {}".format(field_name)))

    @signature.command()
    @CustomChecks.selfbot()
    async def field_content(self, *, field_content: str):
        """Set signature field content"""
        self.config["signature_field_content"] = field_content
        dataIO.save_json(self.config_file, self.config)
        await self.bot.say(chat.info("Signature field content changed to {}".format(field_content)))

    @signature.command(name="color")
    @CustomChecks.selfbot()
    async def _color(self, *, hex_color: str = None):
        """Set signature color

        Uses HEX color"""
        if hex_color is None:
            self.config["signature_colour"] = 0
            dataIO.save_json(self.config_file, self.config)
            await self.bot.say(chat.info("Signature color resetted"))
            return
        pattern = re.compile("^#([A-Fa-f0-9]{6})$")
        if not pattern.match(hex_color):
            await self.bot.say(
                "Looks like the `{}`, that you provided is not color HEX\nOr it is too small/too big.\nExample of "
                "acceptable color HEX: `#1A2B3C`".format(hex_color))
            return
        color = hex_to_rgb(hex_color)
        color = get_int_from_rgb(color)
        self.config["signature_colour"] = color
        dataIO.save_json(self.config_file, self.config)
        await self.bot.say(chat.info("Signature color changed to {} ({})".format(hex_color, chat.inline(color))))

    @commands.command(pass_context=True)
    @commands.has_permissions(embed_links=True)
    @CustomChecks.selfbot()
    async def signed(self, ctx, *, message: str = None):
        """Says something with embedded signature

        Text changeable in config.json"""
        em = discord.Embed(title=self.config["signature_title"], description=self.config["signature_desc"],
                           url=self.config["signature_url"], colour=self.config["signature_colour"],
                           timestamp=ctx.message.timestamp)
        em.add_field(name=self.config["signature_field_name"], value=self.config["signature_field_content"],
                     inline=False)
        em.set_footer(text=ctx.message.author.nick or ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await self.bot.say(message, embed=em)

    # @commands.command(pass_context=True)
    # async def embed(self, ctx, *, message: str):
    #     """Says something via embed
    #     Useful for using emojis on any server without Nitro
    #
    #     Inline code markdown at start and at end of message will be removed"""
    #     if not ctx.message.channel.permissions_for(ctx.message.author).embed_links:
    #         await self.bot.say("Not allowed to send embeds here. Lack `Embed Links` permission")
    #         return
    #     message = re.sub(r'^\s*(`\s*)?|(\s*`)?\s*$', '', message)
    #     if ctx.message.server:
    #         em_color = ctx.message.author.colour
    #     else:
    #         em_color = discord.Colour.default()
    #     em = discord.Embed(description=message, colour=em_color)
    #     await self.bot.say(embed=em)

    # @commands.command(pass_context=True)
    # async def quote(self, ctx, messageid: str, *, response: str = None):
    #     """Quote an message by id"""
    #     message = discord.utils.get(self.bot.messages, id=messageid)
    #     if message is None:
    #         await self.bot.say("Failed to get message with id `" + messageid + "`")
    #     else:
    #         if message.channel.is_private:
    #             colour = discord.Colour.default()
    #             name = message.author.name
    #         else:
    #             colour = message.author.colour
    #             name = message.author.nick or message.author.name
    #         em = discord.Embed(description=message.content, colour=colour, timestamp=message.timestamp)
    #         em.set_author(name=name, icon_url=message.author.avatar_url)
    #         em.set_footer(text=message.author.name + "#" + message.author.discriminator)
    #         attachment = discord.utils.get(message.attachments)
    #         if attachment is not None:
    #             attachment = dict(attachment)
    #             em.set_image(url=attachment['url'])
    #         if ctx.message.channel.permissions_for(ctx.message.server.me).embed_links:
    #             await self.bot.say(response, embed=em)
    #         else:
    #             await self.bot.say((response or "") + "\n\n**Quote from " + message.author.name + "#" +
    #                                message.author.discriminator + ":**\n```\n" + message.content + "```")

    @commands.command(pass_context=True, no_pm=True, aliases=['emojiinfo', 'emojinfo'])
    async def emoji(self, ctx, *, emoji: discord.Emoji):
        """Get info about emoji
        
        Works only with nonstandard emojis (non-unicode)"""
        em = discord.Embed(title=emoji.name, colour=random.randint(0, 16777215))
        em.add_field(name="ID", value=emoji.id)
        em.add_field(name="Has existed since", value=emoji.created_at.strftime('%d.%m.%Y %H:%M:%S %Z'))
        em.add_field(name="\":\" required", value=bool_emojify(emoji.require_colons))
        em.add_field(name="Managed", value=bool_emojify(emoji.managed))
        em.add_field(name="Server", value=emoji.server)
        if emoji.roles:
            em.add_field(name="Roles", value="\n".join([x.name for x in emoji.roles]))
        em.set_image(url=emoji.url)
        if ctx.message.channel.permissions_for(ctx.message.server.me).embed_links:
            await self.bot.say(embed=em)
        else:
            await self.bot.say("```\n" +
                               "ID: " + emoji.id +
                               "\nHas existed since: " + emoji.created_at.strftime('%d.%m.%Y %H:%M:%S %Z') +
                               "\n\":\" required: " + bool_emojify(emoji.require_colons) +
                               "\nManaged: " + bool_emojify(emoji.managed) +
                               "\nServer: " + str(emoji.server) +
                               "\nRoles: " + "\n".join([x.name for x in emoji.roles]) +
                               "```" +
                               emoji.url)

    @commands.command(name='thetime')
    async def _thetime(self):
        """Send bot's current time"""
        await self.bot.say(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S %Z'))

    @commands.command(pass_context=True, aliases=['HEX', 'hex'])
    async def color(self, ctx, color: discord.Color):
        """Shows some info about provided color"""
        color = str(color)
        colorrgb = hex_to_rgb(color)
        colorint = get_int_from_rgb(colorrgb)
        colorhsv = colorsys.rgb_to_hsv(colorrgb[0], colorrgb[1], colorrgb[2])
        colorhls = colorsys.rgb_to_hls(colorrgb[0], colorrgb[1], colorrgb[2])
        coloryiq = colorsys.rgb_to_yiq(colorrgb[0], colorrgb[1], colorrgb[2])
        colorcmyk = rgb_to_cmyk(colorrgb[0], colorrgb[1], colorrgb[2])
        em = discord.Embed(title=str(color),
                           description="Provided HEX: " + color + "\nRGB: " + str(colorrgb) + "\nCMYK: " + str(
                               colorcmyk) + "\nHSV: " + str(colorhsv) + "\nHLS: " + str(colorhls) + "\nYIQ: " + str(
                               coloryiq) + "\nint: " + str(colorint),
                           url='http://www.color-hex.com/color/' + str(color.lstrip('#')), colour=colorint,
                           timestamp=ctx.message.timestamp)
        em.set_thumbnail(url="https://xenforo.com/rgba.php?r={}&g={}&b={}&a=255"
                         .format(colorrgb[0], colorrgb[1], colorrgb[2]))
        if ctx.message.channel.permissions_for(ctx.message.server.me).embed_links:
            await self.bot.say(embed=em)
        else:
            await self.bot.say("```\n" +
                               "Provided HEX: " + color +
                               "\nRGB: " + str(colorrgb) +
                               "\nCMYK: " + str(colorcmyk) +
                               "\nHSV: " + str(colorhsv) +
                               "\nHLS: " + str(colorhls) +
                               "\nYIQ: " + str(coloryiq) +
                               "\nint: " + str(colorint) +
                               "```")

    @commands.command(pass_context=True, no_pm=True)
    async def someone(self, ctx, *, text: str = None):
        """Help I've fallen and I need @someone.

        Discord 2018 April Fools"""
        smilies = ["¯\\_(ツ)_/¯", "(∩ ͡° ͜ʖ ͡°)⊃━☆ﾟ. o ･ ｡ﾟ", "(∩ ͡° ͜ʖ ͡°)⊃━✿✿✿✿✿✿", "༼ つ ◕_◕ ༽つ", "(◕‿◕✿)",
                   "(⁄ ⁄•⁄ω⁄•⁄ ⁄)", "(╯°□°）╯︵ ┻━┻", "ಠ_ಠ", "¯\\(°_o)/¯", "（✿ ͡◕ ᴗ◕)つ━━✫・o。", "ヽ༼ ಠ益ಠ ༽ﾉ"]
        smile = random.choice(smilies)
        member = await self.random_channel_member(ctx.message.channel)
        await self.bot.say("**@someone** {} ***{}*** {}".format(smile,
                                                                chat.escape(member.display_name, mass_mentions=True),
                                                                chat.escape(text, mass_mentions=True) if text else ""))

    async def random_channel_member(self, channel: discord.Channel):
        """Returns random member that has access to channel"""
        randommember = random.choice(list(channel.server.members))
        if channel.permissions_for(randommember).read_messages:
            return randommember
        return await self.random_channel_member(channel)


def check_folders():
    if not os.path.exists("data/moreutils"):
        os.makedirs("data/moreutils")


def check_files():
    system = {"signature_title": "Username",
              "signature_desc": "From Selfbot",
              "signature_url": "http://google.com",
              "signature_colour": 0,
              "signature_field_name": "\"Sometimes, i dream about cheese\"",
              "signature_field_content": "Some text about cheese"}

    f = "data/moreutils/config.json"
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, system)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(MoreUtils(bot))
