import discord
from redbot.core import commands, Config, checks
from redbot.core.utils.embed import randomize_colour
from redbot.core.utils.menus import menu, prev_page, next_page
from discord.ext import tasks

from .utils import badEmbed, goodEmbed, get_league_emoji, get_rank_emoji, get_brawler_emoji
from .utils import remove_codes, calculate_starpoints, get_gamemode_id, get_gamemode_emoji, club_status

from random import choice
import asyncio
import brawlstats
from typing import Union
from re import sub
import datetime
import aiohttp
from cachetools import TTLCache
from fuzzywuzzy import process
from operator import itemgetter, attrgetter

class BrawlStarsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=5245652)
        default_user = {"tag": None, "alt": None}
        self.config.register_user(**default_user)
        default_guild = {"clubs": {}}
        self.config.register_guild(**default_guild)
        self.blacklist_conf = Config.get_conf(None, identifier=42424269, cog_name="Blacklist")
        self.maps = None
        self.aiohttp_session = aiohttp.ClientSession()
        asyncio.ensure_future(self.start_tasks())

    def cog_unload(self):
        self.sortroles.cancel()
        self.sortrolesasia.cancel()
        self.sortrolesbd.cancel()
        self.sortrolesspain.cancel()
        self.sortrolesportugal.cancel()
        self.sortrolesevents.cancel()
        self.sortrolesaquaunited.cancel()
        self.sortroleslatam.cancel()

    async def start_tasks(self):
        await asyncio.sleep(3*60)
        self.sortroles.start()
        await asyncio.sleep(15*60)
        self.sortrolesasia.start()
        await asyncio.sleep(10*60)
        self.sortrolesbd.start()
        await asyncio.sleep(10*60)
        self.sortrolesspain.start()
        await asyncio.sleep(10*60)
        self.sortrolesportugal.start()
        await asyncio.sleep(10*60)
        self.sortrolesevents.start()
        await asyncio.sleep(10*60)
        self.sortrolesaquaunited.start()
        await asyncio.sleep(10*60)
        self.sortroleslatam.start()

    async def initialize(self):
        ofcbsapikey = await self.bot.get_shared_api_tokens("ofcbsapi")
        if ofcbsapikey["api_key"] is None:
            raise ValueError(
                "The Official Brawl Stars API key has not been set.")
        self.ofcbsapi = brawlstats.Client(
            ofcbsapikey["api_key"], is_async=True)
        self.ofcbsapi.cache = TTLCache(10000, 60*10)
        self.starlist_key = (await self.bot.get_shared_api_tokens("starlist"))["starlist"]
        
    async def starlist_request(self, url):
        header = {"Authorization": f"Bearer {self.starlist_key}"}
        async with self.aiohttp_session.get(url, headers=header) as resp:
            return await resp.json()

    def get_blacklist_config(self):
        if self.blacklist_conf is None:
            self.blacklist_conf = Config.get_conf(None, identifier=42424269, cog_name="Blacklist")
        return self.blacklist_conf
        
    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == 680113859759308910 and msg.author.id != 599286708911210557:
            try:
                id = int(msg.content)
                user = self.bot.get_user(int(msg.content))
                if user is None:
                    await (self.bot.get_channel(680113859759308910)).send(".")
                tag = await self.config.user(user).tag()
                if tag is None:
                    await (self.bot.get_channel(680113859759308910)).send(".")
                else:
                    await (self.bot.get_channel(680113859759308910)).send(tag.upper())
            except ValueError:
                pass
            
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 401883208511389716:
            tag = await self.config.user(member).tag()
            if tag is not None:
                ch = member.guild.get_channel(547087959015292929)
                embed = discord.Embed(colour=discord.Colour.blue(), description=f"#{tag.upper()}")
                embed.set_author(name=member.display_name, icon_url=member.avatar_url)
                await asyncio.sleep(3)
                await ch.send(embed=embed)
        elif member.guild.id == 616673259538350084:
            tag = await self.config.user(member).tag()
            if tag is not None:
                ch = member.guild.get_channel(616696393729441849)
                embed = discord.Embed(colour=discord.Colour.blue(), description=f"#{tag.upper()}")
                embed.set_author(name=member.display_name, icon_url=member.avatar_url)
                await asyncio.sleep(3)
                await ch.send(embed=embed)
        elif member.guild.id == 674348799673499671:
            tag = await self.config.user(member).tag()
            if tag is not None:
                ch = member.guild.get_channel(674348799673499671)
                embed = discord.Embed(colour=discord.Colour.blue(), description=f"#{tag.upper()}")
                embed.set_author(name=member.display_name, icon_url=member.avatar_url)
                await asyncio.sleep(3)
                await ch.send(embed=embed)

    @commands.command(aliases=['bssave'])
    async def save(self, ctx, tag, member: discord.Member = None):
        """Save your Brawl Stars player tag"""
        member = ctx.author if member is None else member

        tag = tag.lower().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        try:
            player = await self.ofcbsapi.get_player(tag)
            await self.config.user(member).tag.set(tag.replace("#", ""))
            await ctx.send(embed=goodEmbed(f"BS account {player.name} was saved to {member.name}"))

        except brawlstats.errors.NotFoundError:
            await ctx.send(embed=badEmbed("No player with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            await ctx.send("**Something went wrong, please send a personal message to LA Modmail bot or try again!****")

    @commands.command(aliases=['bssave2'])
    async def savealt(self, ctx, tag, member: discord.Member = None):
        """Save your second Brawl Stars player tag"""
        member = ctx.author if member is None else member

        tag = tag.lower().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        try:
            player = await self.ofcbsapi.get_player(tag)
            await self.config.user(member).alt.set(tag.replace("#", ""))
            await ctx.send(embed=goodEmbed(f"BS account {player.name} was saved to {member.name}"))

        except brawlstats.errors.NotFoundError:
            await ctx.send(embed=badEmbed("No player with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            await ctx.send("**Something went wrong, please send a personal message to LA Modmail bot or try again!****")

    @commands.has_permissions(administrator = True)
    @commands.command(aliases=['bsunsave'])
    async def unsave(self, ctx, member: discord.Member):
        await self.config.user(member).clear()
        await ctx.send("Done.")
            
    @commands.command(aliases=['rbs'])
    async def renamebs(self, ctx, member: discord.Member = None, club_name:bool = True):
        """Change a name of a user to be nickname|club_name"""
        await ctx.trigger_typing()
        prefix = ctx.prefix
        member = ctx.author if member is None else member
        
        if ctx.author != member and ctx.author.top_role < member.top_role:
            return await ctx.send("You can't do this!")

        tag = await self.config.user(member).tag()
        if tag is None:
            return await ctx.send(embed=badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))

        player = await self.ofcbsapi.get_player(tag)
        if "name" in player.raw_data["club"] and club_name:
            nick = f"{player.name} | {player.club.name}"
        else:
            nick = f"{player.name}"
        try:
            await member.edit(nick=nick[:31])
            await ctx.send(f"Done! New nickname: `{nick[:31]}`")
        except discord.Forbidden:
            await ctx.send(f"I dont have permission to change nickname of this user!")
        except Exception as e:
            await ctx.send(f"Something went wrong: {str(e)}")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['p', 'bsp', 'stats'])
    async def profile(self, ctx, *, member: Union[discord.Member, str] = None):
        """View player's BS statistics"""
        await ctx.trigger_typing()
        prefix = ctx.prefix
        tag = ""

        member = ctx.author if member is None else member

        if isinstance(member, discord.Member):
            tag = await self.config.user(member).tag()
            if tag is None:
                return await ctx.send(embed=badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))
        elif member.startswith("#"):
            tag = member.upper().replace('O', '0')
        else:
            try:
                member = self.bot.get_user(int(member))
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(embed=badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))
            except ValueError:
                member = discord.utils.get(ctx.guild.members, name=member)
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(embed=badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))

        if tag is None or tag == "":
            desc = "/p\n/bsprofile @user\n/p discord_name\n/p discord_id\n/p #BSTAG"
            embed = discord.Embed(
                title="Invalid argument!",
                colour=discord.Colour.red(),
                description=desc)
            return await ctx.send(embed=embed)

        if type(member) == discord.Member and await self.config.user(member).alt() is not None:
            tagg = await self.config.user(member).tag()
            altt = await self.config.user(member).alt()
            tagg = "#" + tagg
            altt = "#" + altt
            prompt = await ctx.send(embed=discord.Embed(colour=discord.Colour.blue(),
                                                        title="Which one of the accounts would you like to see?", description=f":one: {tagg.upper()}\n:two: {altt.upper()}"))
            await prompt.add_reaction("<:one1:736684730635780127>")
            await prompt.add_reaction("<:two2:736684762944634891>")

            def check(reaction, user):
                return (user == member or user.id == 230947675837562880) and str(reaction.emoji) in ["<:one1:736684730635780127>", "<:two2:736684762944634891>"]

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                return await prompt.delete()

            if str(reaction.emoji) == "<:one1:736684730635780127>":
                tag = await self.config.user(member).tag()
            elif str(reaction.emoji) == "<:two2:736684762944634891>":
                tag = await self.config.user(member).alt()

            await prompt.delete()

        try:
            player = await self.ofcbsapi.get_player(tag)

        except brawlstats.errors.NotFoundError:
            return await ctx.send(embed=badEmbed("No player with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            return await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            return await ctx.send("****Something went wrong, please send a personal message to LA Modmail bot or try again!****")

        colour = player.name_color if player.name_color is not None else "0xffffffff"
        embed = discord.Embed(color=discord.Colour.from_rgb(
            int(colour[4:6], 16), int(colour[6:8], 16), int(colour[8:10], 16)))
        player_icon_id = player.raw_data["icon"]["id"]
        icons = await self.starlist_request("https://api.starlist.pro/icons")
        player_icon = icons['player'][str(player_icon_id)]['imageUrl2']
        embed.set_author(
            name=f"{player.name} {player.raw_data['tag']}",
            icon_url=player_icon if icons['status'] == 'ok' else member.avatar_url)
        embed.add_field(
            name="Trophies",
            value=f"{get_league_emoji(player.trophies)} {player.trophies} (<:starpoint:661265872891150346> {calculate_starpoints(player)})")
        embed.add_field(
            name="Highest Trophies",
            value=f"{get_league_emoji(player.highest_trophies)} {player.highest_trophies}")
        embed.add_field(
            name="Level",
            value=f"<:exp:614517287809974405> {player.exp_level}")
        star_powers = sum([len(x.star_powers) for x in player.brawlers])
        gadgets = sum([len(x['gadgets']) for x in player.raw_data['brawlers']])
        embed.add_field(
            name="Unlocked Brawlers",
            value=f"<:brawlers:614518101983232020> {len(player.brawlers)} <:star_power:729732781638156348> {star_powers} <:gadget:716341776608133130> {gadgets}")
        if "tag" in player.raw_data["club"]:
            embed.add_field(
                name="Club",
                value=f"<:bsband:600741378497970177> {player.club.name}")
            try:
                club = await self.ofcbsapi.get_club(player.club.tag)
                for m in club.members:
                    if m.tag == player.raw_data['tag']:
                        embed.add_field(name="Role", value=f"<:role:614520101621989435> {m.role.capitalize()}")
                        break
            except brawlstats.errors.RequestError:
                embed.add_field(
                    name="Role",
                    value=f"<:offline:642094554019004416> Error while retrieving role")
        else:
            embed.add_field(
                name="Club",
                value=f"<:noclub:661285120287834122> Not in a club")
        embed.add_field(
            name="3v3 Wins",
            value=f"{get_gamemode_emoji(get_gamemode_id('gemgrab'))} {player.raw_data['3vs3Victories']}")
        embed.add_field(
            name="Showdown Wins",
            value=f"{get_gamemode_emoji(get_gamemode_id('showdown'))} {player.solo_victories} {get_gamemode_emoji(get_gamemode_id('duoshowdown'))} {player.duo_victories}")
        rr_levels = ["-", "Normal", "Hard", "Expert", "Master", "Insane"]
        if player.best_robo_rumble_time > 5:
            rr_level = f"Insane {player.best_robo_rumble_time - 5}"
        else:
            rr_level = rr_levels[player.best_robo_rumble_time]
        embed.add_field(
            name="Best RR Level",
            value=f"{get_gamemode_emoji(get_gamemode_id('roborumble'))} {rr_level}")
        #embed.add_field(
        #    name="Best Time as Big Brawler",
        #    value=f"<:biggame:614517022323245056> {player.best_time_as_big_brawler//60}:{str(player.best_time_as_big_brawler%60).rjust(2, '0')}")
        title_extra = ""
        value_extra = ""
        if "highestPowerPlayPoints" in player.raw_data:
            title_extra = " (Highest)"
            value_extra = f" ({player.raw_data['highestPowerPlayPoints']})"
        if "powerPlayPoints" in player.raw_data:
            embed.add_field(
                name=f"Power Play Points{title_extra}",
                value=f"<:powertrophies:661266876235513867> {player.raw_data['powerPlayPoints']}{value_extra}")
        else:
            embed.add_field(name=f"Power Play Points{title_extra}",
                            value=f"<:powertrophies:661266876235513867> 0 {value_extra}")
        emo = "<:good:450013422717763609> Qualified" if player.raw_data['isQualifiedFromChampionshipChallenge'] else "<:bad:450013438756782081> Not qualified"
        embed.add_field(
            name="Championship",
            value=f"{emo}")
        texts = [
            "Check out all your brawlers using /brawlers!", 
            "Want to see your club stats? Try /club!", 
            "Have you seen all our clubs? No? Do /clubs!",
            "You can see stats of other players by typing /p @user.",
            "You can display player's stats by using his tag! /p #TAG",
            "Did you know LA Bot can display CR stats as well? /crp"
        ]
        embed.set_footer(text=choice(texts))
        await ctx.send(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['b'])
    async def brawlers(self, ctx, *, member: Union[discord.Member, str] = None):
        """Brawl Stars brawlers"""
        await ctx.trigger_typing()
        prefix = ctx.prefix
        tag = ""
        member = ctx.author if member is None else member

        if isinstance(member, discord.Member):
            tag = await self.config.user(member).tag()
            if tag is None:
                return await ctx.send(embed=badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))
        elif member.startswith("#"):
            tag = member.upper().replace('O', '0')
        else:
            try:
                member = discord.utils.get(ctx.guild.members, id=int(member))
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(
                            embed=badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))
            except ValueError:
                member = discord.utils.get(ctx.guild.members, name=member)
                if member is not None:
                    tag = await self.config.user(member).tag()
                    if tag is None:
                        return await ctx.send(
                            embed=badEmbed(f"This user has no tag saved! Use {prefix}bssave <tag>"))

        if tag is None or tag == "":
            desc = "/b\n/brawlers @user\n/b discord_name\n/b discord_id\n/b #BSTAG"
            embed = discord.Embed(
                title="Invalid argument!",
                colour=discord.Colour.red(),
                description=desc)
            return await ctx.send(embed=embed)

        if await self.config.user(member).alt() is not None:
            tagg = await self.config.user(member).tag()
            altt = await self.config.user(member).alt()
            tagg = "#" + tagg
            altt = "#" + altt
            prompt = await ctx.send(embed=discord.Embed(colour=discord.Colour.blue(),
                                                        title="Which one of the accounts would you like to see?", description=f":one: {tagg.upper()}\n:two: {altt.upper()}"))
            await prompt.add_reaction("<:one1:736684730635780127>")
            await prompt.add_reaction("<:two2:736684762944634891>")

            def check(reaction, user):
                return (user == member or user.id == 230947675837562880) and str(reaction.emoji) in ["<:one1:736684730635780127>", "<:two2:736684762944634891>"]

            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=60)
            except asyncio.TimeoutError:
                return await prompt.delete()

            if str(reaction.emoji) == "<:one1:736684730635780127>":
                tag = await self.config.user(member).tag()
            elif str(reaction.emoji) == "<:two2:736684762944634891>":
                tag = await self.config.user(member).alt()

            await prompt.delete()

        try:
            player = await self.ofcbsapi.get_player(tag)

        except brawlstats.errors.NotFoundError:
            return await ctx.send(embed=badEmbed("No player with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            return await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            return await ctx.send(
                "****Something went wrong, please send a personal message to LA Modmail bot or try again!****")

        colour = player.name_color if player.name_color is not None else "0xffffffff"

        player_icon_id = player.raw_data["icon"]["id"]
        icons = await self.starlist_request("https://api.starlist.pro/icons")
        player_icon = icons['player'][str(player_icon_id)]['imageUrl2']

        brawlers = player.raw_data['brawlers']
        brawlers.sort(key=itemgetter('trophies'), reverse=True)

        embedfields = []
        
        for c, br in enumerate(brawlers, start=1):
            rank = discord.utils.get(self.bot.emojis, name=f"rank_{br['rank']}")
            ename = f"{get_brawler_emoji(br['name'])} {br['name'].lower().title()} "
            ename += f"<:pp:664267845336825906> {br['power']}"
            evalue = f"{rank} `{br['trophies']}/{br['highestTrophies']}`\n"
            evalue += f"<:star_power:729732781638156348> `{len(br['starPowers'])}` "
            evalue += f"<:gadget:716341776608133130> `{len(br['gadgets'])}`"
            evalue = evalue.strip()
            embedfields.append([ename, evalue])
        
        embedstosend = []
        for i in range(0, len(embedfields), 15):
            embed = discord.Embed(color=discord.Colour.from_rgb(int(colour[4:6], 16), int(colour[6:8], 16), int(colour[8:10], 16)), title=f"Brawlers({len(brawlers)}/38):")
            embed.set_author(name=f"{player.name} {player.raw_data['tag']}", icon_url=player_icon)
            for e in embedfields[i:i + 15]:
                embed.add_field(name=e[0], value=e[1], inline=True)
            embedstosend.append(embed)

        for i in range(len(embedstosend)):
            embedstosend[i].set_footer(text=f"Page {i+1}/{len(embedstosend)}\n/brawler <name> for more stats")

        if len(embedstosend) > 1:
            await menu(ctx, embedstosend, {"⬅": prev_page, "➡": next_page, }, timeout=2000)
        else:
            await ctx.send(embed=embedstosend[0])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(aliases=['br'])
    async def brawler(self, ctx, brawler: str, member: Union[discord.Member, str] = None):
        """Brawler specific info"""
        await ctx.trigger_typing()
        prefix = ctx.prefix
        member = ctx.author if member is None else member
                
        try:
            member.id
        except AttributeError:
            return await ctx.send(embed=badEmbed(f"No such brawler found! If the brawler's name contains spaces surround it with quotes!"))

        tag = await self.config.user(member).tag()
        if tag is None:
            return await ctx.send(embed=badEmbed(f"You have no tag saved! Use {prefix}save <tag>"))

        if tag is None or tag == "":
            desc = "/p\n/profile @user\n/p discord_name\n/p discord_id\n/p #BSTAG"
            embed = discord.Embed(
                title="Invalid argument!",
                colour=discord.Colour.red(),
                description=desc)
            return await ctx.send(embed=embed)

        try:
            player = await self.ofcbsapi.get_player(tag)
            brawler_data = (await self.starlist_request("https://api.starlist.pro/brawlers"))['list']

        except brawlstats.errors.NotFoundError:
            return await ctx.send(embed=badEmbed("No player with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            return await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            return await ctx.send(
                "****Something went wrong, please send a personal message to LA Modmail bot or try again!****")

        unlocked = False
        br = None
        for b in player.raw_data['brawlers']:
            if b['name'] == brawler.upper():
                br = b
                unlocked = True
                break

        data = None
        for b in brawler_data:
            if b['name'].upper() == brawler.upper():
                data = b
                break

        if br is None and data is None:
            return await ctx.send(embed=badEmbed(f"No such brawler found! If the brawler's name contains spaces surround it with quotes!"))

        colour = player.name_color if player.name_color is not None else "0xffffffff"
        embed = discord.Embed(color=discord.Colour.from_rgb(
            int(colour[4:6], 16), int(colour[6:8], 16), int(colour[8:10], 16)))
        if unlocked:
            embed.set_author(name=f"{player.name}'s {data['name']}", icon_url=data['imageUrl2'])
        else:
            embed.set_author(name=f"{data['name']} (Not unlocked)", icon_url=data['imageUrl2'])
        embed.description = f"<:brawlers:614518101983232020> {data['rarity']}"
        if unlocked:
            rank = discord.utils.get(self.bot.emojis, name=f"rank_{br['rank']}")
            embed.description += f" {rank} {br.get('trophies')}/{br['highestTrophies']}"
            embed.description += f" <:pp:664267845336825906> {br['power']}"
        embed.description += "\n```" + data['description'] + "```"
        embed.set_footer(text=data['class'])
        starpowers = ""
        gadgets = ""
        for star in data['starPowers']:
            owned = False
            if unlocked:
                for sp in br['starPowers']:
                    if star['id'] == sp['id']:
                        owned = True
            emoji = "<:star_power:729732781638156348>" if owned else "<:sp_locked:729751963549302854>"
            starpowers += f"{emoji} {star['name']}\n`{star['description']}`\n"
        embed.add_field(name="Star Powers", value=starpowers)
        
        for gadget in data['gadgets']:
            owned = False
            if unlocked:
                for ga in br['gadgets']:
                    if gadget['id'] == ga['id']:
                        owned = True
            emoji = "<:gadget:716341776608133130>" if owned else "<:ga_locked:729752493793476759>"
            gadgets += f"{emoji} {gadget['name']}\n`{gadget['description']}`\n"
        embed.add_field(name="Gadgets", value=gadgets)
        await ctx.send(embed=embed)
    
    def time_left(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        if hours <= 24:
            return "{}h {:02}m".format(int(hours), int(minutes))
        else:
            return f"{int(hours)//24}d {(int(hours)//24)%24}h"
                       
    @commands.command(aliases=['e'])
    async def events(self, ctx):
        events = await self.starlist_request("https://api.starlist.pro/events")
        if events['status'] != "ok":
            return await ctx.send(embed=badEmbed("Something went wrong. Please try again later!"))
        time_now = datetime.datetime.now()
        embed = discord.Embed(title="EVENTS", colour=discord.Colour.green())
        active = ""
        for ev in events['active']:
            if ev['slot']['name'] == "Duo Showdown":
                continue
            modifier = ""
            powerplay = ""
            if ev['slot']['name'] == "Power Play":
                powerplay = "<:powertrophies:661266876235513867> "
            if ev['modifier'] is not None:
                modifier = f"↳ Modifier: {ev['modifier']['name']}\n"
            active += f"**{powerplay}{get_gamemode_emoji(ev['map']['gameMode']['id'])} {ev['map']['gameMode']['name']}**\n↳ Map: {ev['map']['name']}\n{modifier}"
        embed.add_field(name="ACTIVE", value=active, inline=False)
        upcoming = ""
        for ev in events['upcoming']:
            if ev['slot']['name'] == "Duo Showdown":
                continue
            modifier = ""
            powerplay = ""
            if ev['slot']['name'] == "Power Play":
                powerplay = "<:powertrophies:661266876235513867> "
            if ev['modifier'] is not None:
                modifier = f"↳ Modifier: {ev['modifier']['name']}\n"
            start = datetime.datetime.strptime(ev['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
            diff = self.time_left((start - time_now).total_seconds())
            upcoming += f"**{powerplay}{get_gamemode_emoji(ev['map']['gameMode']['id'])} {ev['map']['gameMode']['name']}**\n↳ Map: {ev['map']['name']}\n↳ Starts in: {diff}\n{modifier}"
        embed.add_field(name="UPCOMING", value=upcoming, inline=False)
        embed.set_footer(text="Data provided by starlist.pro")
        await ctx.send(embed=embed)
                        
    @commands.command(aliases=['m'])
    async def map(self, ctx, *, map_name: str):
        if self.maps is None:
            final = {}
            all_maps = await self.starlist_request("https://api.starlist.pro/maps")
            for m in all_maps['list']:
                final[m['hash']] = {'url': m['imageUrl'], 'name': m['name'], 
                                   'disabled': m['disabled'], 'link': m['link'],
                                   'gm_url': m['gameMode']['imageUrl'], 'id': m['id']}
            self.maps = final
                        
        map_name = map_name.replace(" ", "-")
        result = process.extract(map_name, list(self.maps.keys()), limit=1)
        result_map = self.maps[result[0][0]]
        embed = discord.Embed(colour=discord.Colour.green() )
        embed.set_author(name=result_map['name'], url=result_map['link'], icon_url=result_map['gm_url'])
        data = (await self.starlist_request(f"https://api.starlist.pro/maps/{result_map['id']}/300-599"))['map']
        brawlers = (await self.starlist_request(f"https://api.starlist.pro/brawlers"))['list']
        stats = data['stats']
        
        if len(stats) > 0 and 'winRate' in stats[0]:
            wr = ""
            stats.sort(key=itemgetter('winRate'), reverse=True)
            for counter, br in enumerate(stats[:10], start=1):
                name = None
                for b in brawlers:
                    if b['id'] == br['brawler']:
                        name = b['name'].upper()
                        break
                if name is None:
                    continue                               
                wr += f"{get_brawler_emoji(name)} `{int(br['winRate'])}%` "
                if counter % 5 == 0:
                    wr += "\n"
            embed.add_field(name="Best Win Rates", value=wr, inline=False)
                   
        if len(stats) > 0 and 'bossWinRate' in stats[0]:
            bwr = ""
            stats.sort(key=itemgetter('bossWinRate'), reverse=True)
            for counter, br in enumerate(stats[:10], start=1):
                name = None
                for b in brawlers:
                    if b['id'] == br['brawler']:
                        name = b['name'].upper()
                        break
                if name is None:
                    continue                               
                bwr += f"{get_brawler_emoji(name)} `{int(br['bossWinRate'])}%` "
                if counter % 5 == 0:
                    bwr += "\n"
            embed.add_field(name="Best Boss Win Rates", value=bwr, inline=False)
                  
        if len(stats) > 0 and 'useRate' in stats[0]:
            ur = ""
            stats.sort(key=itemgetter('useRate'), reverse=True)
            for counter, br in enumerate(stats[:10], start=1):
                name = None
                for b in brawlers:
                    if b['id'] == br['brawler']:
                        name = b['name'].upper()
                        break
                if name is None:
                    continue                               
                ur += f"{get_brawler_emoji(name)} `{int(br['useRate'])}%` "
                if counter % 5 == 0:
                    ur += "\n"
            embed.add_field(name="Highest Use Rates", value=ur, inline=False)
                                            
        if result_map['disabled']:
            embed.description = "This map is currently disabled."
        embed.set_footer(text="Data provided by starlist.pro")
        embed.set_image(url=result_map['url'])
        await ctx.send(embed=embed)
       
    #some day maybe
    def get_badge(self, badge_id):
        guild = self.bot.get_guild(717766786019360769)
        em = discord.utils.get(guild.emojis, name=str(badge_id))
        return str(em)
    
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command()
    async def club(self, ctx, key: Union[discord.Member, str] = None, keyword = None):
        """View players club or club saved in a server"""
        await ctx.trigger_typing()
        if key is None:
            mtag = await self.config.user(ctx.author).tag()
            if mtag is None:
                return await ctx.send(embed=badEmbed(f"You have no tag saved! Use {ctx.prefix}bssave <tag>"))
            try:
                player = await self.ofcbsapi.get_player(mtag)
                if not "tag" in player.raw_data["club"]:
                    return await ctx.send("This user is not in a club!")
                tag = player.club.tag
            except brawlstats.errors.RequestError as e:
                await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        elif isinstance(key, discord.Member):
            member = key
            mtag = await self.config.user(member).tag()
            if mtag is None:
                return await ctx.send(embed=badEmbed(f"This user has no tag saved! Use {ctx.prefix}bssave <tag>"))
            try:
                player = await self.ofcbsapi.get_player(mtag)
                if not "tag" in player.raw_data["club"]:
                    return await ctx.send("This user is not in a club!")
                tag = player.club.tag
            except brawlstats.errors.RequestError as e:
                await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))
        elif key.startswith("#"):
            tag = key.upper().replace('O', '0')
        else:
            tag = await self.config.guild(ctx.guild).clubs.get_raw(key.lower(), "tag", default=None)
            if tag is None:
                return await ctx.send(embed=badEmbed(f"{key.title()} isn't saved club in this server!"))
        try:
            club = await self.ofcbsapi.get_club(tag)

        except brawlstats.errors.NotFoundError:
            return await ctx.send(embed=badEmbed("No club with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))
            return

        if keyword is None:
            if club.description is not None:
                embed = discord.Embed(description=f"```{club.description}```")
            else:
                embed = discord.Embed(description="```None```")
            embed.set_author(name=f"{club.name} {club.tag}")
            embed.add_field(
                name="Total Trophies",
                value=f"<:bstrophy:552558722770141204> `{club.trophies}`")
            embed.add_field(
                name="Required Trophies",
                value=f"{get_league_emoji(club.required_trophies)} `{club.required_trophies}`")
            embed.add_field(
                name="Average Trophies",
                value=f"<:bstrophy:552558722770141204> `{club.trophies//len(club.members)}`")
            for m in club.members:
                if m.role == "president":
                    embed.add_field(
                        name="President",
                        value=f"{get_league_emoji(m.trophies)}`{m.trophies}` {m.name}")
                    break
            embed.add_field(
                name="Members",
                value=f"<:icon_gameroom:553299647729238016> {len(club.members)}/100")
            embed.add_field(
                name="Status",
                value=f"{club_status[club.type.lower()]['emoji']} {club_status[club.type.lower()]['name']}"
            )
            topm = ""
            for m in club.members[:5]:
                topm += f"{get_league_emoji(m.trophies)}`{m.trophies}` {remove_codes(m.name)}\n"
            worstm = ""
            for m in club.members[-5:]:
                worstm += f"{get_league_emoji(m.trophies)}`{m.trophies}` {remove_codes(m.name)}\n"
            embed.add_field(name="Top Members", value=topm, inline=True)
            embed.add_field(name="Lowest Members", value=worstm, inline=True)
            return await ctx.send(embed=randomize_colour(embed))
        elif keyword in ["memberlist", "members", "list", "m"]:
            colour = choice([discord.Colour.green(),
                             discord.Colour.blue(),
                             discord.Colour.purple(),
                             discord.Colour.orange(),
                             discord.Colour.red(),
                             discord.Colour.teal()])
            startingembed = discord.Embed(colour=colour, title=f"{club.name} {club.tag}")
            mems = {}
            embedfields = []
            rank = 1
            for mem in club.members:
                if mem.role.lower() == 'vicepresident':
                    mems.update({f"{get_league_emoji(mem.trophies)}`{mem.trophies}`**{remove_codes(mem.name)}** {mem.tag}": "vp"})
                elif mem.role.lower() == 'president':
                    mems.update({f"{get_league_emoji(mem.trophies)}`{mem.trophies}`**{remove_codes(mem.name)}** {mem.tag}" : "pres"})
                elif mem.role.lower() == 'senior':
                    mems.update({f"{get_league_emoji(mem.trophies)}`{mem.trophies}`**{remove_codes(mem.name)}** {mem.tag}" : "senior"})
                elif mem.role.lower() == 'member':
                    mems.update({f"{get_league_emoji(mem.trophies)}`{mem.trophies}`**{remove_codes(mem.name)}** {mem.tag}" : "member"})
                e_name = f"__**{rank}**__ {remove_codes(mem.name)}: {mem.tag}"
                e_value= f" {get_league_emoji(mem.trophies)}`{mem.trophies}` <:role:739089429599354921>  ️{mem.role.capitalize()}"
                rank = rank + 1
                embedfields.append([e_name, e_value])

            senior_count = 0
            vp_count = 0
            pres_value = ""
            vp_value = ""
            senior_value = ""
            for item in mems.items():
                if item[1] == "pres":
                    pres_value = item[0]
                elif item[1] == "vp":
                    vp_count = vp_count + 1
                    vp_value = vp_value + f"{item[0]}\n"
                elif item[1] == "senior":
                    senior_count = senior_count + 1
                    senior_value = senior_value + f"{item[0]}\n"

            startingembed.add_field(name="President", value=pres_value)
            if vp_value == "":
                startingembed.add_field(name=f"Vice Presidents: {vp_count}", value="None", inline=False)
            else:
                startingembed.add_field(name=f"Vice Presidents: {vp_count}", value=vp_value, inline=False)
            if senior_value == "":
                startingembed.add_field(name=f"Seniors: {senior_count}", value="None", inline=False)
            elif len(senior_value) > 1024:
                startingembed.add_field(name=f"Seniors: {senior_count}", value="Too many to show", inline=False)
            else:
                startingembed.add_field(name=f"Seniors: {senior_count}", value=senior_value, inline=False)

            embedstosend = []
            embedstosend.append(startingembed)
            for i in range(0, len(embedfields), 19):
                embed = discord.Embed(color=colour, title=f"{club.name} {club.tag}")
                for e in embedfields[i:i + 19]:
                    embed.add_field(name=e[0], value=e[1], inline=False)
                embedstosend.append(embed)

            for i in range(len(embedstosend)):
                embedstosend[i].set_footer(text=f"Page {i + 1}/{len(embedstosend)}\nScroll down for the full member list")

            if len(embedstosend) > 1:
                await menu(ctx, embedstosend, {"⬆️": prev_page, "⬇️": next_page, }, timeout=2000)
            else:
                await ctx.send(embed=embedstosend[0])
        elif keyword == "log":
            url = "https://api.starlist.pro/clublog/" + club.tag.replace("#", "")
            log = await self.starlist_request(url)
            if log['status'] != "ok":
                return await ctx.send(embed=badEmbed("Something went wrong. Please try again later!"))
            msg = ""
            for h in log['history']:
                time = h['timeFormat']
                if h['type'] == "members":
                    name = h['data']['player']['name']
                    tag = "#" + h['data']['player']['tag']
                    addition = f"<:yesconfirm:595535992329601034> **{name} ({tag}) joined!** {time}\n" if h["data"]["joined"] else f"<:nocancel:595535992199315466> **{name} ({tag}) left!** {time}\n"
                elif h['type'] == 'settings':
                    if h['data']['type'] == "description":
                        dold = h['data']['old']
                        dnew = h['data']['new']
                        addition = f"🛠️ **Description changed from `{dold}` to `{dnew}`!** {time}\n"
                    elif h['data']['type'] == "requirement":
                        old = h['data']['old']
                        new = h['data']['new']
                        addition = f"🛠️ **Requirement changed from `{old}` to `{new}`!** {time}\n"
                    elif h['data']['type'] == "status":
                        sold = h['data']['old']
                        snew = h['data']['new']
                        addition = f"🛠️ **Status changed from `{sold}` to `{snew}`!** {time}\n"
                    else:
                        stype = h['data']['type']
                        addition = f"Unrecognized setting type: {stype}\n"
                elif h['type'] == "roles":
                    continue
                    if h['data']['promote']:
                        action = "promoted"
                        emoji = "<:upvote:554429793446395904>"
                    else:
                        action = "demoted"
                        emoji = "<:downvote:554429867752685569>"
                    rname = h['data']['player']['name']
                    rtag = "#" + h['data']['player']['tag']
                    rold = h['data']['old']
                    rnew = h['data']['new']
                    addition = f"{emoji} **{rname} {rtag} {action} from {rold} to {rnew}!** {time}\n"
                else:
                    type = h['type']
                    addition = f"Unrecognized type: {type}\n"
                if len(msg) + len(addition) > 2024:
                    break
                msg += addition

            colour = choice([discord.Colour.green(),
                             discord.Colour.blue(),
                             discord.Colour.purple(),
                             discord.Colour.orange(),
                             discord.Colour.red(),
                             discord.Colour.teal()])

            embed = discord.Embed(colour=colour, title=f"{club.name} {club.tag}", description=msg)
            embed.set_footer(text="Data provided by starlist.pro")

            await ctx.send(embed=embed)

        else:
            return await ctx.send(embed=badEmbed(f"There's no such keyword: {keyword}."))

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.guild_only()
    @commands.group(invoke_without_command=True)
    async def clubs(self, ctx, *, keyword: str = ""):
        """View all clubs saved in a server"""
        offline = False
        low_clubs = False
        roles = False
        skip_errors = False
        reverse_order = False
        await ctx.trigger_typing()
        if "offline" in keyword:
            offline = True
            keyword = keyword.replace("offline", "").strip()

        if "low" in keyword:
            low_clubs = True
            keyword = keyword.replace("low", "").strip()

        if "roles" in keyword:
            roles = True
            keyword = keyword.replace("roles", "").strip()

        if "skiperrors" in keyword:
            skip_errors = True
            keyword = keyword.replace("skiperrors", "").strip()

        if "reverse" in keyword:
            reverse_order = True
            keyword = keyword.replace("reverse", "").strip()

        if len((await self.config.guild(ctx.guild).clubs()).keys()) < 1:
            return await ctx.send(
                embed=badEmbed(f"This server has no clubs saved. Save a club by using {ctx.prefix}clubs add!"))

        loadingembed = discord.Embed(colour=discord.Colour.red(),
                                     description="Requesting clubs. Might take a while.\n(0%)", title="Loading...")
        msg = await ctx.send(embed=loadingembed)

        saved_clubs = await self.config.guild(ctx.guild).clubs()

        try:
            clubs = []
            keys = saved_clubs.keys()
            for ind, key in enumerate(keys):
                if offline:
                    break
                if keyword == "":
                    try:
                        club = await self.ofcbsapi.get_club(saved_clubs[key]['tag'])
                    except brawlstats.errors.RequestError as e:
                        if skip_errors:
                            continue
                        else:
                            offline = True
                            break
                    clubs.append(club)
                elif keyword != "":
                    if "family" in saved_clubs[key] and saved_clubs[key]['family'] == keyword:
                        club = await self.ofcbsapi.get_club(saved_clubs[key]['tag'])
                        clubs.append(club)
                if not offline:
                    if 0 <= ind / len(keys) <= 0.25:
                        if loadingembed.description != "Requesting clubs. Might take a while.\n(25%) ────":
                            loadingembed = discord.Embed(colour=discord.Colour.red(),
                                                            description="Requesting clubs. Might take a while.\n(25%) ────",
                                                            title="Loading...")
                            await msg.edit(embed=loadingembed)
                    elif 0.25 <= ind / len(keys) <= 0.5:
                        if loadingembed.description != "Requesting clubs. Might take a while.\n(50%) ────────":
                            loadingembed = discord.Embed(colour=discord.Colour.red(),
                                                            description="Requesting clubs. Might take a while.\n(50%) ────────",
                                                            title="Loading...")
                            await msg.edit(embed=loadingembed)
                    elif 0.5 <= ind / len(keys) <= 0.75:
                        if loadingembed.description != "Requesting clubs. Might take a while.\n(75%) ────────────":
                            loadingembed = discord.Embed(colour=discord.Colour.red(),
                                                            description="Requesting clubs. Might take a while.\n(75%) ────────────",
                                                            title="Loading...")
                            await msg.edit(embed=loadingembed)
                    elif 0.75 <= ind / len(keys) <= 1:
                        if loadingembed.description != "Requesting clubs. Might take a while.\n(100%) ────────────────":
                            loadingembed = discord.Embed(colour=discord.Colour.red(),
                                                            description="Requesting clubs. Might take a while.\n(100%) ────────────────",
                                                            title="Loading...")
                            await msg.edit(embed=loadingembed)
                #await asyncio.sleep(0.3)

            embedFields = []

            loadingembed = discord.Embed(colour=discord.Colour.red(), description="Almost there!", title="Creating the embed...")
            if not offline:
                await msg.edit(embed=loadingembed)
                clubs = sorted(clubs, key=lambda sort: (sort.trophies), reverse=not reverse_order)

                for i in range(len(clubs)):
                    key = ""
                    for k in saved_clubs.keys():
                        if clubs[i].tag.replace("#", "") == saved_clubs[k]['tag']:
                            key = k
                    
                    saved_clubs[key]['lastMemberCount'] = len(clubs[i].members)
                    saved_clubs[key]['lastRequirement'] = clubs[i].required_trophies
                    saved_clubs[key]['lastScore'] = clubs[i].trophies
                    saved_clubs[key]['lastPosition'] = i
                    saved_clubs[key]['lastStatus'] = clubs[i].type
                    
                    info = saved_clubs[key]["info"] if "info" in saved_clubs[key] else ""
                    role = ctx.guild.get_role(saved_clubs[key]["role"]) if "role" in saved_clubs[key] else None

                    if low_clubs and len(clubs[i].members) >= 95:
                        continue

                    e_name = f"<:bsband:600741378497970177> {clubs[i].name} [{key}] {clubs[i].tag} {info}"
                    role_info = f"{role.mention}\n" if roles and role is not None else ""
                    e_value = f"{role_info}{club_status[clubs[i].type.lower()]['emoji']} <:bstrophy:552558722770141204>`{clubs[i].trophies}` {get_league_emoji(clubs[i].required_trophies)}"
                    e_value += f"`{clubs[i].required_trophies}+` <:icon_gameroom:553299647729238016>`{len(clubs[i].members)}`"
                    embedFields.append([e_name, e_value])

                await self.config.guild(ctx.guild).set_raw("clubs", value=saved_clubs)

            else:
                await msg.edit(embed=loadingembed)
                offclubs = []
                for k in saved_clubs.keys():
                    offclubs.append([saved_clubs[k]['lastPosition'], k])
                offclubs = sorted(offclubs, key=lambda x: x[0], reverse=not reverse_order)

                for club in offclubs:
                    ckey = club[1]
                    cscore = saved_clubs[ckey]['lastScore']
                    cname = saved_clubs[ckey]['name']
                    ctag = saved_clubs[ckey]['tag']
                    cinfo = saved_clubs[ckey]['info']
                    cmembers = saved_clubs[ckey]['lastMemberCount']
                    creq = saved_clubs[ckey]['lastRequirement']
                    ctype = saved_clubs[ckey]['lastStatus']

                    if low_clubs and cmembers >= 95:
                        continue

                    e_name = f"<:bsband:600741378497970177> {cname} [{ckey}] #{ctag} {cinfo}"
                    e_value = f"{club_status[ctype.lower()]['emoji']} <:bstrophy:552558722770141204>`{cscore}` {get_league_emoji(creq)}`{creq}+` <:icon_gameroom:553299647729238016>`{cmembers}` "
                    embedFields.append([e_name, e_value])

            colour = choice([discord.Colour.green(),
                             discord.Colour.blue(),
                             discord.Colour.purple(),
                             discord.Colour.orange(),
                             discord.Colour.red(),
                             discord.Colour.teal()])
            embedsToSend = []
            for i in range(0, len(embedFields), 8):
                embed = discord.Embed(colour=colour)
                embed.set_author(
                    name=f"{ctx.guild.name} clubs",
                    icon_url=ctx.guild.icon_url)
                page = (i // 8) + 1
                footer = f"[{page}/{len(embedFields)//8+1}] API is offline, showing last saved data." if offline else f"[{page}/{len(embedFields)//8+1}] Need more info about a club? Use {ctx.prefix}club [key]"
                embed.set_footer(text=footer)
                for e in embedFields[i:i + 8]:
                    embed.add_field(name=e[0], value=e[1], inline=False)
                embedsToSend.append(embed)

            if len(embedsToSend) > 1:
                await msg.delete()
                await menu(ctx, embedsToSend, {"⬅": prev_page, "➡": next_page, }, timeout=2000)
            elif len(embedsToSend) == 1:
                await msg.delete()
                await ctx.send(embed=embedsToSend[0])
            else:
                await msg.delete()
                await ctx.send("No clubs found!")

        except ZeroDivisionError as e:
            return await ctx.send(
                "**Something went wrong, please send a personal message to LA Modmail bot or try again!**")

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @clubs.command(name="add")
    async def clans_add(self, ctx, key: str, tag: str):
        """
        Add a club to /clubs command
        key - key for the club to be used in other commands
        tag - in-game tag of the club
        """
        await ctx.trigger_typing()
        if tag.startswith("#"):
            tag = tag.strip('#').upper().replace('O', '0')

        if key in (await self.config.guild(ctx.guild).clubs()).keys():
            return await ctx.send(embed=badEmbed("This club is already saved!"))

        try:
            club = await self.ofcbsapi.get_club(tag)
            result = {
                "name": club.name,
                "nick": key.title(),
                "tag": club.tag.replace("#", ""),
                "lastMemberCount": club.members_count,
                "lastRequirement": club.required_trophies,
                "lastScore": club.trophies,
                "lastStatus" : club.type,
                "info": "",
                "role": None
            }
            key = key.lower()
            await self.config.guild(ctx.guild).clubs.set_raw(key, value=result)
            await ctx.send(embed=goodEmbed(f"{club.name} was successfully saved in this server!"))

        except brawlstats.errors.NotFoundError as e:
            await ctx.send(embed=badEmbed("No club with this tag found, try again!"))

        except brawlstats.errors.RequestError as e:
            await ctx.send(embed=badEmbed(f"BS API is offline, please try again later! ({str(e)})"))

        except Exception as e:
            return await ctx.send("**Something went wrong, please send a personal message to LA Modmail bot or try again!**")

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @clubs.command(name="remove")
    async def clubs_remove(self, ctx, key: str):
        """
        Remove a club from /clubs command
        key - key for the club used in commands
        """
        await ctx.trigger_typing()
        key = key.lower()

        try:
            name = await self.config.guild(ctx.guild).clubs.get_raw(key, "name")
            await self.config.guild(ctx.guild).clubs.clear_raw(key)
            await ctx.send(embed=goodEmbed(f"{name} was successfully removed from this server!"))
        except KeyError:
            await ctx.send(embed=badEmbed(f"{key.title()} isn't saved club!"))

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @clubs.command(name="info")
    async def clubs_info(self, ctx, key: str, *, info: str = ""):
        """Edit club info"""
        await ctx.trigger_typing()
        key = key.lower()

        try:
            await self.config.guild(ctx.guild).clubs.set_raw(key, "info", value=info)
            await ctx.send(embed=goodEmbed("Club info successfully edited!"))
        except KeyError:
            await ctx.send(embed=badEmbed(f"{key.title()} isn't saved club in this server!"))

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @clubs.command(name="role")
    async def clubs_role(self, ctx, key: str, role: discord.Role = None):
        """Add a role to club"""
        await ctx.trigger_typing()
        key = key.lower()

        try:
            if await self.config.guild(ctx.guild).clubs.get_raw(key, "tag") is None:
                return await ctx.send(embed=badEmbed(f"{key.title()} isn't saved club in this server!"))
            await self.config.guild(ctx.guild).clubs.set_raw(key, "role", value=role.id if role is not None else None)
            name = role.name if role is not None else "None"
            await ctx.send(embed=goodEmbed(f"Club role set to {name}!"))
        except KeyError:
            await ctx.send(embed=badEmbed(f"{key.title()} isn't saved club in this server!"))

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @clubs.command(name="family")
    async def clubs_family(self, ctx, key: str, *, family: str = ""):
        """Edit club's family"""
        await ctx.trigger_typing()
        try:
            await self.config.guild(ctx.guild).clubs.set_raw(key, "family", value=family)
            await ctx.send(embed=goodEmbed("Club family successfully edited!"))
        except KeyError:
            await ctx.send(embed=badEmbed(f"{key.title()} isn't saved club in this server!"))

    async def removeroleifpresent(self, member: discord.Member, *roles):
        msg = ""
        for role in roles:
            if role is None:
                continue
            if role in member.roles:
                await member.remove_roles(role)
                msg += f"Removed **{str(role)}**\n"
        return msg

    async def addroleifnotpresent(self, member: discord.Member, *roles):
        msg = ""
        for role in roles:
            if role is None:
                continue
            if role not in member.roles:
                await member.add_roles(role)
                msg += f"Added **{str(role)}**\n"
        return msg

    @tasks.loop(hours=4)
    async def sortroles(self):
        ch = self.bot.get_channel(653295573872672810)
        await ch.trigger_typing()
        labs = ch.guild.get_role(576028728052809728)
        guest = ch.guild.get_role(578260960981286923)
        newcomer = ch.guild.get_role(534461445656543255)
        brawlstars = ch.guild.get_role(576002604740378629)
        vp = ch.guild.get_role(536993652648574976)
        pres = ch.guild.get_role(536993632918568991)
        error_counter = 0

        for member in ch.guild.members:
            if member.bot:
                continue
            tag = await self.config.user(member).tag()
            if tag is None:
                msg = ""
                if pres in member.roles or vp in member.roles:
                    msg += "Has President or VP role, no tag saved.\n"
                    msg += await self.removeroleifpresent(member, vp, pres)
                    try:
                        await member.send(f"Hello {member.mention},\nyour (Vice)President role in LA Brawl Stars server has been removed.\nThe reason is you don't have your in-game tag saved at LA bot. You can fix it by saving your tag using `/save #YOURTAG`.\n")
                    except (discord.HTTPException, discord.Forbidden) as e:
                        msg += f"Couldn't send a DM with info. {str(e)}\n"
                    await ch.send(embed=discord.Embed(colour=discord.Colour.red(), description=msg, title=str(member), timestamp=datetime.datetime.now()))
                continue
            try:
                player = await self.ofcbsapi.get_player(tag)
                await asyncio.sleep(0.3)
            except brawlstats.errors.RequestError as e:
                await ch.send(embed=discord.Embed(colour=discord.Colour.red(), description=f"{str(member)} ({member.id}) #{tag}"))
                error_counter += 1 
                if error_counter == 10:
                    await ch.send(embed=discord.Embed(colour=discord.Colour.red(), description=f"Stopping after 10 request errors! Displaying the last one:\n({str(e)})"))
                    break
                await asyncio.sleep(1)
                continue
            except Exception as e:
                return await ch.send(embed=discord.Embed(colour=discord.Colour.red(), description=f"**Something went wrong while requesting {tag}!**\n({str(e)})"))

            msg = ""
            player_in_club = "name" in player.raw_data["club"]
            member_roles = []
            member_role = None
            member_role_expected = None

            for role in member.roles:
                if role.name.startswith('LA '):
                    member_roles.append(role)

            if len(member_roles) > 1:
                msg += f"Found more than one club role. (**{', '.join([str(r) for r in member_roles])}**)\n"
                for role in member_roles:
                    if sub(r'[^\x00-\x7f]', r'', role.name).strip() != sub(r'[^\x00-\x7f]', r'', player.club.name).strip():
                        msg += await self.removeroleifpresent(member, role)
            
            member_role = None if len(member_roles) < 1 else member_roles[0]

            if not player_in_club:
                msg += await self.removeroleifpresent(member, labs, vp, pres, newcomer)
                msg += await self.addroleifnotpresent(member, guest)
                if member_role is not None:
                    msg += await self.removeroleifpresent(member, member_role)

            if player_in_club and not player.club.name.startswith("LA "):
                msg += await self.removeroleifpresent(member, labs, vp, pres, newcomer, member_role)
                msg += await self.addroleifnotpresent(member, guest, brawlstars)

            if player_in_club and player.club.name.startswith("LA "):
                for role in ch.guild.roles:
                    if sub(r'[^\x00-\x7f]', r'', role.name).strip() == sub(r'[^\x00-\x7f]', r'', player.club.name).strip():
                        member_role_expected = role
                        break
                if member_role_expected is None:
                    await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=f"Role for the club {player.club.name} not found.", title=str(member), timestamp=datetime.datetime.now()))
                    continue
                msg += await self.removeroleifpresent(member, guest, newcomer)
                msg += await self.addroleifnotpresent(member, labs, brawlstars)
                if member_role is None:
                    msg += await self.addroleifnotpresent(member, member_role_expected)
                elif member_role != member_role_expected:
                    msg += await self.removeroleifpresent(member, member_role)
                    msg += await self.addroleifnotpresent(member, member_role_expected)
                try:
                    await asyncio.sleep(0.2)
                    player_club = await self.ofcbsapi.get_club(player.club.tag)
                    for mem in player_club.members:
                        if mem.tag == player.raw_data['tag']:
                            if mem.role.lower() == 'vicepresident':
                                msg += await self.addroleifnotpresent(member, vp)
                                msg += await self.removeroleifpresent(member, pres)
                            elif mem.role.lower() == 'president':
                                msg += await self.addroleifnotpresent(member, pres)
                                msg += await self.removeroleifpresent(member, vp)
                            elif mem.role.lower() == 'member':
                                msg += await self.removeroleifpresent(member, vp, pres)
                            break
                except brawlstats.errors.RequestError:
                    pass
            if msg != "":
                await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member), timestamp=datetime.datetime.now()))

    @sortroles.before_loop
    async def before_sortroles(self):
        await asyncio.sleep(5)

    @tasks.loop(hours=4)
    async def sortrolesasia(self):
        ch = self.bot.get_channel(672267298001911838)
        await ch.trigger_typing()
        lafamily = ch.guild.get_role(663795352666636305)
        guest = ch.guild.get_role(663798304194166854)
        newcomer = ch.guild.get_role(663799853889093652)
        vp = ch.guild.get_role(663793699972579329)
        pres = ch.guild.get_role(663793444199596032)
        leadership = ch.guild.get_role(663910848569409598)
        leadershipemb = ch.guild.get_role(673177525396176927)
        error_counter = 0

        for member in ch.guild.members:
            if member.bot:
                continue
            tag = await self.config.user(member).tag()
            if tag is None:
                continue
            try:
                player = await self.ofcbsapi.get_player(tag)
                await asyncio.sleep(0.3)
            except brawlstats.errors.RequestError as e:
                error_counter += 1
                if error_counter == 5:
                    await ch.send(embed=discord.Embed(colour=discord.Colour.red(), description=f"Stopping after 20 request errors! Displaying the last one:\n({str(e)})"))
                    break
                await asyncio.sleep(1)
                continue
            except Exception as e:
                return await ch.send(embed=discord.Embed(colour=discord.Colour.red(), description=f"**Something went wrong while requesting {tag}!**\n({str(e)})"))

            msg = ""
            player_in_club = "name" in player.raw_data["club"]
            member_roles = []
            member_role = None
            member_role_expected = None
            tags = []
            guilds = await self.config.all_guilds()
            asia = guilds[663716223258984496]
            clubs = asia["clubs"]
            for club in clubs:
                info = clubs[club]
                tag = "#" + info["tag"]
                tags.append(tag)

            for role in member.roles:
                if role.name.startswith('LA ') and role.id != 682056906222993446:
                    member_roles.append(role)

            if len(member_roles) > 1:
                msg += f"**{str(member)}** has more than one club role. Removing **{', '.join([str(r) for r in member_roles])}**"
                member_role = member_roles[0]
                for role in member_roles[1:]:
                    msg += await self.removeroleifpresent(member, role)

            member_role = None if len(member_roles) < 1 else member_roles[0]

            if not player_in_club:
                msg += await self.removeroleifpresent(member, lafamily, vp, pres, newcomer)
                msg += await self.addroleifnotpresent(member, guest)
                if member_role is not None:
                    msg += await self.removeroleifpresent(member, member_role)

            if player_in_club and player.club.tag not in tags:
                msg += await self.removeroleifpresent(member, lafamily, vp, pres, newcomer, leadership, leadershipemb)
                msg += await self.addroleifnotpresent(member, guest)
                if member_role is not None:
                    msg += await self.removeroleifpresent(member, member_role)

            if player_in_club and player.club.tag in tags:
                for role in ch.guild.roles:
                    if sub(r'[^\x00-\x7f]', r'', role.name).strip() == sub(
                            r'[^\x00-\x7f]', r'', player.club.name).strip():
                        member_role_expected = role
                        break
                if member_role_expected is None:
                    msg += await self.removeroleifpresent(member, guest, newcomer, vp, pres, leadership, leadershipemb)
                    msg += await self.addroleifnotpresent(member, lafamily)
                    if msg != "":
                        await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member)))
                    continue
                msg += await self.removeroleifpresent(member, guest, newcomer)
                msg += await self.addroleifnotpresent(member, lafamily)
                if member_role is None:
                    msg += await self.addroleifnotpresent(member, member_role_expected)
                elif member_role != member_role_expected:
                    msg += await self.removeroleifpresent(member, member_role)
                    msg += await self.addroleifnotpresent(member, member_role_expected)
                try:
                    await asyncio.sleep(0.3)
                    player_club = await self.ofcbsapi.get_club(player.club.tag)
                    for mem in player_club.members:
                        if mem.tag == player.raw_data['tag']:
                            if mem.role.lower() == 'vicepresident':
                                msg += await self.addroleifnotpresent(member, vp, leadership, leadershipemb)
                                msg += await self.removeroleifpresent(member, pres)
                            elif mem.role.lower() == 'president':
                                msg += await self.addroleifnotpresent(member, pres, leadership, leadershipemb)
                                msg += await self.removeroleifpresent(member, vp)
                            elif mem.role.lower() == 'member':
                                msg += await self.removeroleifpresent(member, vp, pres, leadership, leadershipemb)
                            break
                except brawlstats.errors.RequestError:
                    pass
            if msg != "":
                await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member)))

    @sortrolesasia.before_loop
    async def before_sortrolesasia(self):
        await asyncio.sleep(5)

    @tasks.loop(hours=8)
    async def sortrolesbd(self):
        ch = self.bot.get_channel(690881058756886599)
        await ch.trigger_typing()
        bs = ch.guild.get_role(678062773938159627)
        lamember = ch.guild.get_role(678062771069517825)
        newcomer = ch.guild.get_role(678623072143540225)
        guest = ch.guild.get_role(678062759711211546)
        pres = ch.guild.get_role(678062737338793984)
        vp = ch.guild.get_role(678062737963614211)
        leadership = ch.guild.get_role(690872028474900550)
        zerotwo = ch.guild.get_role(691297688297406596)
        twofour = ch.guild.get_role(678062784834961436)
        foursix = ch.guild.get_role(678062785049133129)
        sixeight = ch.guild.get_role(678062785917354035)
        eightten = ch.guild.get_role(678062786508750859)
        tenthirteen = ch.guild.get_role(678062788480073739)
        thirteensixteen = ch.guild.get_role(678062787267788801)
        sixteentwenty = ch.guild.get_role(678062787867443211)
        twenty = ch.guild.get_role(691297775626879007)
        error_counter = 0

        for member in ch.guild.members:
            if member.bot:
                continue
            tag = await self.config.user(member).tag()
            if tag is None:
                continue
            try:
                player = await self.ofcbsapi.get_player(tag)
                await asyncio.sleep(0.3)
            except brawlstats.errors.RequestError as e:
                error_counter += 1
                if error_counter == 5:
                    await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                      description=f"Stopping after 5 request errors! Displaying the last one:\n({str(e)})"))
                    break
                await asyncio.sleep(1)
                continue
            except Exception as e:
                return await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                         description=f"**Something went wrong while requesting {tag}!**\n({str(e)})"))

            msg = ""
            player_in_club = "name" in player.raw_data["club"]
            member_roles = []
            member_role = None
            member_role_expected = None

            if player.trophies < 2000:
                msg += await self.addroleifnotpresent(member, zerotwo)
                msg += await self.removeroleifpresent(member, twofour, foursix, sixeight, eightten, tenthirteen, thirteensixteen, sixteentwenty, twenty)
            elif 2000 <= player.trophies < 4000:
                msg += await self.addroleifnotpresent(member, twofour)
                msg += await self.removeroleifpresent(member, zerotwo, foursix, sixeight, eightten, tenthirteen,
                                                      thirteensixteen, sixteentwenty, twenty)
            elif 4000 <= player.trophies < 6000:
                msg += await self.addroleifnotpresent(member, foursix)
                msg += await self.removeroleifpresent(member, twofour, zerotwo, sixeight, eightten, tenthirteen,
                                                      thirteensixteen, sixteentwenty, twenty)
            elif 6000 <= player.trophies < 8000:
                msg += await self.addroleifnotpresent(member, sixeight)
                msg += await self.removeroleifpresent(member, twofour, foursix, zerotwo, eightten, tenthirteen,
                                                      thirteensixteen, sixteentwenty, twenty)
            elif 8000 <= player.trophies < 10000:
                msg += await self.addroleifnotpresent(member, eightten)
                msg += await self.removeroleifpresent(member, twofour, foursix, sixeight, zerotwo, tenthirteen,
                                                      thirteensixteen, sixteentwenty, twenty)
            elif 10000 <= player.trophies < 13000:
                msg += await self.addroleifnotpresent(member, tenthirteen)
                msg += await self.removeroleifpresent(member, twofour, foursix, sixeight, eightten, zerotwo,
                                                      thirteensixteen, sixteentwenty, twenty)
            elif 13000 <= player.trophies < 16000:
                msg += await self.addroleifnotpresent(member, thirteensixteen)
                msg += await self.removeroleifpresent(member, twofour, foursix, sixeight, eightten, tenthirteen,
                                                      zerotwo, sixteentwenty, twenty)
            elif 16000 <= player.trophies < 20000:
                msg += await self.addroleifnotpresent(member, sixteentwenty)
                msg += await self.removeroleifpresent(member, twofour, foursix, sixeight, eightten, tenthirteen,
                                                      thirteensixteen, zerotwo, twenty)
            elif 20000 <= player.trophies:
                msg += await self.addroleifnotpresent(member, twenty)
                msg += await self.removeroleifpresent(member, twofour, foursix, sixeight, eightten, tenthirteen,
                                                      thirteensixteen, sixteentwenty, zerotwo)

            for role in member.roles:
                if role.name.startswith('LA '):
                    member_roles.append(role)

            if len(member_roles) > 1:
                msg += f"Found more than one club role. (**{', '.join([str(r) for r in member_roles])}**)\n"
                for role in member_roles:
                    if sub(r'[^\x00-\x7f]', r'', role.name).strip() != sub(r'[^\x00-\x7f]', r'',
                                                                           player.club.name).strip():
                        msg += await self.removeroleifpresent(member, role)

            member_role = None if len(member_roles) < 1 else member_roles[0]

            if not player_in_club:
                msg += await self.removeroleifpresent(member, lamember, vp, pres, leadership, newcomer)
                msg += await self.addroleifnotpresent(member, guest)
                if member_role is not None:
                    msg += await self.removeroleifpresent(member, member_role)

            if player_in_club and not player.club.name.startswith("LA "):
                msg += await self.removeroleifpresent(member, lamember, vp, pres, leadership, newcomer)
                msg += await self.addroleifnotpresent(member, guest, bs)
                if member_role is not None:
                    msg += await self.removeroleifpresent(member, member_role)

            if player_in_club and player.club.name.startswith("LA "):
                for role in ch.guild.roles:
                    if sub(r'[^\x00-\x7f]', r'', role.name).strip() == sub(r'[^\x00-\x7f]', r'',
                                                                           player.club.name).strip():
                        member_role_expected = role
                        break
                msg += await self.removeroleifpresent(member, guest, newcomer)
                msg += await self.addroleifnotpresent(member, lamember, bs)
                if member_role is None:
                    msg += await self.addroleifnotpresent(member, member_role_expected)
                elif member_role != member_role_expected:
                    msg += await self.removeroleifpresent(member, member_role)
                    msg += await self.addroleifnotpresent(member, member_role_expected)
                if member_role_expected is not None:
                    try:
                        await asyncio.sleep(0.3)
                        player_club = await self.ofcbsapi.get_club(player.club.tag)
                        for mem in player_club.members:
                            if mem.tag == player.raw_data['tag']:
                                if mem.role.lower() == 'vicepresident':
                                    msg += await self.addroleifnotpresent(member, vp, leadership)
                                    msg += await self.removeroleifpresent(member, pres)
                                elif mem.role.lower() == 'president':
                                    msg += await self.addroleifnotpresent(member, pres, leadership)
                                    msg += await self.removeroleifpresent(member, vp)
                                elif mem.role.lower() == 'member':
                                    msg += await self.removeroleifpresent(member, vp, pres, leadership)
                                break
                    except brawlstats.errors.RequestError:
                        pass
                elif member_role_expected is None:
                    msg += await self.removeroleifpresent(member, vp, pres, leadership)
            if msg != "":
                await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member),
                                                  timestamp=datetime.datetime.now()))

    @sortrolesbd.before_loop
    async def before_sortrolesbd(self):
        await asyncio.sleep(5)

    @tasks.loop(hours=4)
    async def sortrolesspain(self):
        try:
            ch = self.bot.get_channel(693781513363390475)
            await ch.trigger_typing()
            memberrole = ch.guild.get_role(526805067165073408)
            guest = ch.guild.get_role(574176894627479583)
            newcomer = ch.guild.get_role(569473123942924308)
            otherclubs = ch.guild.get_role(601518751472549918)
            error_counter = 0

            for member in ch.guild.members:
                if member.bot:
                    continue
                tag = await self.config.user(member).tag()
                if tag is None:
                    continue
                try:
                    player = await self.ofcbsapi.get_player(tag)
                    await asyncio.sleep(0.3)
                except brawlstats.errors.RequestError as e:
                    error_counter += 1
                    if error_counter == 10:
                        await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                          description=f"¡Deteniéndose después de 10 errores de solicitud! Mostrando el último: \n({str(e)})"))
                        break
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    return await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                             description=f"**Algo ha ido mal solicitando {tag}!**\n({str(e)})"))



                msg = ""
                player_in_club = "name" in player.raw_data["club"]
                member_roles = []
                member_role = None
                member_role_expected = None

                tags = []
                guilds = await self.config.all_guilds()
                spain = guilds[460550486257565697]
                clubs = spain["clubs"]
                for club in clubs:
                    info = clubs[club]
                    tagn = "#" + info["tag"]
                    tags.append(tagn)

                for role in member.roles:
                    if role.name.startswith('LA '):
                        member_roles.append(role)

                if len(member_roles) > 1:
                    msg += f"Se ha encontrado más de un rol de club. **{', '.join([str(r) for r in member_roles])}**"
                    member_role = member_roles[0]
                    for role in member_roles[1:]:
                        msg += await self.removeroleifpresent(member, role)

                member_role = None if len(member_roles) < 1 else member_roles[0]

                if not player_in_club:
                    msg += await self.removeroleifpresent(member, memberrole, otherclubs, newcomer)
                    msg += await self.addroleifnotpresent(member, guest)
                    if member_role is not None:
                        msg += await self.removeroleifpresent(member, member_role)

                if player_in_club and "LA " not in player.club.name and player.club.tag not in tags:
                    msg += await self.removeroleifpresent(member, memberrole, otherclubs, newcomer)
                    msg += await self.addroleifnotpresent(member, guest)
                    if member_role is not None:
                        msg += await self.removeroleifpresent(member, member_role)

                if player_in_club and "LA " in player.club.name and player.club.tag not in tags:
                    msg += await self.removeroleifpresent(member,  newcomer)
                    msg += await self.addroleifnotpresent(member, memberrole, otherclubs)
                    if member_role is not None:
                        msg += await self.removeroleifpresent(member, member_role)

                if player_in_club and player.club.tag in tags:
                    for role in ch.guild.roles:
                        if sub(r'[^\x00-\x7f]', r'', role.name).strip() == sub(
                                r'[^\x00-\x7f]', r'', player.club.name).strip():
                            member_role_expected = role
                            break
                    msg += await self.removeroleifpresent(member, guest, newcomer)
                    msg += await self.addroleifnotpresent(member, memberrole)
                    if member_role is None:
                        msg += await self.addroleifnotpresent(member, member_role_expected)
                    elif member_role != member_role_expected:
                        msg += await self.removeroleifpresent(member, member_role)
                        msg += await self.addroleifnotpresent(member, member_role_expected)
                if msg != "":
                    await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member)))
        except Exception as e:
            await ch.send(e)


    @sortrolesspain.before_loop
    async def before_sortrolesspain(self):
        await asyncio.sleep(5)

    @tasks.loop(hours=4)
    async def sortrolesportugal(self):
        ch = self.bot.get_channel(712394680389599281)
        await ch.trigger_typing()
        bibi = ch.guild.get_role(713413824878870568)
        revolution = ch.guild.get_role(713413515582373921)
        alpha = ch.guild.get_role(713413699389620305)
        laportugal = ch.guild.get_role(712288417861599242)
        elite = ch.guild.get_role(712288829209575515)
        visitante = ch.guild.get_role(617040783840772241)
        lamember = ch.guild.get_role(712296400473555085)
        vp = ch.guild.get_role(616797458944622623)
        newcomer = ch.guild.get_role(618606684637495306)
        error_counter = 0

        for member in ch.guild.members:
            if member.bot:
                continue
            tag = await self.config.user(member).tag()
            if tag is None:
                continue
            try:
                player = await self.ofcbsapi.get_player(tag)
                await asyncio.sleep(0.3)
            except brawlstats.errors.RequestError as e:
                error_counter += 1
                if error_counter == 5:
                    await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                      description=f"Stopping after 20 request errors! Displaying the last one:\n({str(e)})"))
                    break
                await asyncio.sleep(1)
                continue
            except Exception as e:
                return await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                         description=f"**Something went wrong while requesting {tag}!**\n({str(e)})"))

            msg = ""
            player_in_club = "name" in player.raw_data["club"]

            tags = []
            guilds = await self.config.all_guilds()
            portugal = guilds[616673259538350084]
            clubs = portugal["clubs"]
            for club in clubs:
                info = clubs[club]
                tagn = "#" + info["tag"]
                tags.append(tagn)

            if not player_in_club:
                msg += await self.removeroleifpresent(member, laportugal, elite, lamember, vp, newcomer)
                msg += await self.addroleifnotpresent(member, visitante)

            if player_in_club and "LA " not in player.club.name and player.club.tag not in tags:
                msg += await self.removeroleifpresent(member, laportugal, elite, lamember, vp, newcomer)
                msg += await self.addroleifnotpresent(member, visitante)

            if player_in_club and "LA " in player.club.name and player.club.tag not in tags:
                msg += await self.removeroleifpresent(member, laportugal, elite, visitante, vp, newcomer)
                msg += await self.addroleifnotpresent(member, lamember)

            if player_in_club and player.club.tag in tags:
                msg += await self.removeroleifpresent(member, lamember, visitante, newcomer)
                if player.club.name == "LA Portugal":
                    msg += await self.removeroleifpresent(member, elite, revolution, bibi, alpha)
                    msg += await self.addroleifnotpresent(member, laportugal)
                elif player.club.name == "LA Elite":
                    msg += await self.removeroleifpresent(member, laportugal, revolution, bibi, alpha)
                    msg += await self.addroleifnotpresent(member, elite)
                elif player.club.name == "LA Revolution":
                    msg += await self.removeroleifpresent(member, elite, laportugal, bibi, alpha)
                    msg += await self.addroleifnotpresent(member, revolution)
                elif player.club.name == "LA Bibi":
                    msg += await self.removeroleifpresent(member, elite, revolution, laportugal, alpha)
                    msg += await self.addroleifnotpresent(member, bibi)
                elif player.club.name == "LA Alpha":
                    msg += await self.removeroleifpresent(member, elite, revolution, bibi, laportugal)
                    msg += await self.addroleifnotpresent(member, alpha)
                else:
                    msg += f"Couldn't find a role for {player.club.name}."
                try:
                    player_club = await self.ofcbsapi.get_club(player.club.tag)
                    for mem in player_club.members:
                        if mem.tag == player.raw_data['tag']:
                            if mem.role.lower() == 'vicepresident':
                                msg += await self.addroleifnotpresent(member, vp)
                            else:
                                msg += await self.removeroleifpresent(member, vp)
                            break
                except brawlstats.errors.RequestError:
                    msg += "<:offline:642094554019004416> Couldn't retrieve player's club role."
            if msg != "":
                await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member)))

    @sortrolesportugal.before_loop
    async def before_sortrolesportugal(self):
        await asyncio.sleep(5)

    @tasks.loop(hours=8)
    async def sortrolesevents(self):
        try:
            ch = self.bot.get_channel(707246339133669436)
            await ch.trigger_typing()
            lamember = ch.guild.get_role(654334569528688641)
            guest = ch.guild.get_role(701822453021802596)
            es = ch.guild.get_role(654341494773383178)
            eu = ch.guild.get_role(654342521492865043)
            asia = ch.guild.get_role(654341631302041610)
            latam = ch.guild.get_role(654341685920399381)
            na = ch.guild.get_role(654341571331883010)
            bd = ch.guild.get_role(706469329679417366)
            newcomer = ch.guild.get_role(677272975938027540)
            esg = ch.guild.get_role(704951308154699858)
            eug = ch.guild.get_role(704951500782174268)
            asiag = ch.guild.get_role(704951716071866450)
            latamg = ch.guild.get_role(704951697990221876)
            nag = ch.guild.get_role(704951841229897758)
            error_counter = 0

            for member in ch.guild.members:
                if member.bot:
                    continue
                tag = await self.config.user(member).tag()
                if tag is None:
                    continue
                try:
                    player = await self.ofcbsapi.get_player(tag)
                    await asyncio.sleep(0.3)
                except brawlstats.errors.RequestError as e:
                    error_counter += 1
                    if error_counter == 5:
                        await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                          description=f"Stopping after 20 request errors! Displaying the last one:\n({str(e)})"))
                        break
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    return await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                             description=f"**Something went wrong while requesting {tag}!**\n({str(e)})"))

                msg = ""
                player_in_club = "name" in player.raw_data["club"]

                tags = []
                guilds = await self.config.all_guilds()
                events = guilds[654334199494606848]
                clubs = events["clubs"]
                for club in clubs:
                    info = clubs[club]
                    tagn = "#" + info["tag"]
                    tags.append(tagn)

                if not player_in_club:
                    if es in member.roles:
                        msg += await self.removeroleifpresent(member, es)
                        msg += await self.addroleifnotpresent(member, esg)
                    elif eu in member.roles:
                        msg += await self.removeroleifpresent(member, eu)
                        msg += await self.addroleifnotpresent(member, eug)
                    elif asia in member.roles:
                        msg += await self.removeroleifpresent(member, asia)
                        msg += await self.addroleifnotpresent(member, asiag)
                    elif latam in member.roles:
                        msg += await self.removeroleifpresent(member, latam)
                        msg += await self.addroleifnotpresent(member, latamg)
                    elif na in member.roles:
                        msg += await self.removeroleifpresent(member, na)
                        msg += await self.addroleifnotpresent(member, nag)
                    elif bd in member.roles:
                        msg += await self.removeroleifpresent(member, bd)
                    msg += await self.removeroleifpresent(member, lamember, newcomer)
                    msg += await self.addroleifnotpresent(member, guest)

                if player_in_club and "LA " not in player.club.name and player.club.tag not in tags:
                    if es in member.roles:
                        msg += await self.removeroleifpresent(member, es)
                        msg += await self.addroleifnotpresent(member, esg)
                    elif eu in member.roles:
                        msg += await self.removeroleifpresent(member, eu)
                        msg += await self.addroleifnotpresent(member, eug)
                    elif asia in member.roles:
                        msg += await self.removeroleifpresent(member, asia)
                        msg += await self.addroleifnotpresent(member, asiag)
                    elif latam in member.roles:
                        msg += await self.removeroleifpresent(member, latam)
                        msg += await self.addroleifnotpresent(member, latamg)
                    elif na in member.roles:
                        msg += await self.removeroleifpresent(member, na)
                        msg += await self.addroleifnotpresent(member, nag)
                    elif bd in member.roles:
                        msg += await self.removeroleifpresent(member, bd)
                    msg += await self.removeroleifpresent(member, lamember, newcomer)
                    msg += await self.addroleifnotpresent(member, guest)

                if player_in_club and "LA " in player.club.name and player.club.tag not in tags:
                    if esg in member.roles:
                        msg += await self.removeroleifpresent(member, esg)
                        msg += await self.addroleifnotpresent(member, es)
                    elif eug in member.roles:
                        msg += await self.removeroleifpresent(member, eug)
                        msg += await self.addroleifnotpresent(member, eu)
                    elif asiag in member.roles:
                        msg += await self.removeroleifpresent(member, asiag)
                        msg += await self.addroleifnotpresent(member, asia)
                    elif latamg in member.roles:
                        msg += await self.removeroleifpresent(member, latamg)
                        msg += await self.addroleifnotpresent(member, latam)
                    elif nag in member.roles:
                        msg += await self.removeroleifpresent(member, nag)
                        msg += await self.addroleifnotpresent(member, na)
                    msg += await self.removeroleifpresent(member, guest, newcomer)
                    msg += await self.addroleifnotpresent(member, lamember)

                if player_in_club and player.club.tag in tags:
                    if esg in member.roles:
                        msg += await self.removeroleifpresent(member, esg)
                        msg += await self.addroleifnotpresent(member, es)
                    elif eug in member.roles:
                        msg += await self.removeroleifpresent(member, eug)
                        msg += await self.addroleifnotpresent(member, eu)
                    elif asiag in member.roles:
                        msg += await self.removeroleifpresent(member, asiag)
                        msg += await self.addroleifnotpresent(member, asia)
                    elif latamg in member.roles:
                        msg += await self.removeroleifpresent(member, latamg)
                        msg += await self.addroleifnotpresent(member, latam)
                    elif nag in member.roles:
                        msg += await self.removeroleifpresent(member, nag)
                        msg += await self.addroleifnotpresent(member, na)
                    msg += await self.removeroleifpresent(member, guest, newcomer)
                    msg += await self.addroleifnotpresent(member, lamember)
                if msg != "":
                    await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member)))
        except Exception as e:
            await ch.send(e)

    @sortrolesevents.before_loop
    async def before_sortrolesevents(self):
        await asyncio.sleep(5)

    @tasks.loop(hours=4)
    async def sortrolesaquaunited(self):
        try:
            ch = self.bot.get_channel(711253160999780432)
            await ch.trigger_typing()
            lafam = ch.guild.get_role(635136601034326077)
            viewer = ch.guild.get_role(645274004244004865)
            memberclub = ch.guild.get_role(651116342900031488)
            senior = ch.guild.get_role(631558962050891817)
            aqua = ch.guild.get_role(700698977271808040)
            united = ch.guild.get_role(631166049395539988)
            fury = ch.guild.get_role(703591387970535435)
            arrow = ch.guild.get_role(718138400582008852)
            shade = ch.guild.get_role(720716725766717560)
            newcomer = ch.guild.get_role(631516344684380205)
            minus = ch.guild.get_role(701772917909880892)
            whitelist = ch.guild.get_role(714503658183852052)
            error_counter = 0

            for member in ch.guild.members:
                if member.bot or whitelist in member.roles:
                    continue
                tag = await self.config.user(member).tag()
                if tag is None:
                    continue
                try:
                    player = await self.ofcbsapi.get_player(tag)
                    await asyncio.sleep(0.3)
                except brawlstats.errors.RequestError as e:
                    error_counter += 1
                    if error_counter == 5:
                        await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                          description=f"Stopping after 20 request errors! Displaying the last one:\n({str(e)})"))
                        break
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    return await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                             description=f"**Something went wrong while requesting {tag}!**\n({str(e)})"))

                msg = ""
                player_in_club = "name" in player.raw_data["club"]

                tags = []
                guilds = await self.config.all_guilds()
                aquaunited = guilds[631139200871432198]
                clubs = aquaunited["clubs"]
                for club in clubs:
                    info = clubs[club]
                    tagn = "#" + info["tag"]
                    tags.append(tagn)

                if not player_in_club:
                    msg += await self.removeroleifpresent(member, lafam, memberclub, senior, aqua, united, fury, newcomer, minus)
                    msg += await self.addroleifnotpresent(member, viewer)

                if player_in_club and "LA " not in player.club.name and player.club.tag not in tags:
                    msg += await self.removeroleifpresent(member, lafam, memberclub, senior, aqua, united, fury, newcomer, minus)
                    msg += await self.addroleifnotpresent(member, viewer)

                if player_in_club and "LA " in player.club.name and player.club.tag not in tags:
                    msg += await self.removeroleifpresent(member, viewer, memberclub, senior, aqua, united, fury, newcomer)
                    msg += await self.addroleifnotpresent(member, lafam, minus)

                if player_in_club and player.club.tag in tags:
                    msg += await self.removeroleifpresent(member, lafam, viewer, newcomer)
                    msg += await self.addroleifnotpresent(member, minus)
                    if player.club.name == "LA United":
                        msg += await self.removeroleifpresent(member, aqua, fury, arrow, shade)
                        msg += await self.addroleifnotpresent(member, united)
                    elif player.club.name == "LA Aqua":
                        msg += await self.removeroleifpresent(member, united, fury, arrow, shade)
                        msg += await self.addroleifnotpresent(member, aqua)
                    elif player.club.name == "LA Fury":
                        msg += await self.removeroleifpresent(member, aqua, united, arrow, shade)
                        msg += await self.addroleifnotpresent(member, fury)
                    elif player.club.name == "LA Arrow":
                        msg += await self.removeroleifpresent(member, aqua, united, fury, shade)
                        msg += await self.addroleifnotpresent(member, arrow)
                    elif player.club.name == "LA Shade":
                        msg += await self.removeroleifpresent(member, aqua, united, fury, arrow)
                        msg += await self.addroleifnotpresent(member, shade)
                    else:
                        msg += f"Couldn't find a role for {player.club.name}."
                    try:
                        player_club = await self.ofcbsapi.get_club(player.club.tag)
                        for mem in player_club.members:
                            if mem.tag == player.raw_data['tag']:
                                if mem.role.lower() == 'senior':
                                    msg += await self.removeroleifpresent(member, memberclub)
                                    msg += await self.addroleifnotpresent(member, senior)
                                elif mem.role.lower() == 'member':
                                    msg += await self.removeroleifpresent(member, senior)
                                    msg += await self.addroleifnotpresent(member, memberclub)
                                else:
                                    msg += await self.removeroleifpresent(member, senior, memberclub)
                                break
                    except brawlstats.errors.RequestError:
                        msg += "<:offline:642094554019004416> Couldn't retrieve player's club role."
                if msg != "":
                    await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member)))
        except Exception as e:
            await ch.send(e)

    @sortrolesaquaunited.before_loop
    async def before_sortrolesaquaunited(self):
        await asyncio.sleep(5)

    @tasks.loop(hours=8)
    async def sortroleslatam(self):
        ch = self.bot.get_channel(711070847841992796)
        await ch.trigger_typing()
        derucula = ch.guild.get_role(632420307872907295)
        overlay = ch.guild.get_role(705795922067718234)
        cl = ch.guild.get_role(700896108745982023)
        co = ch.guild.get_role(700895961551077387)
        uy = ch.guild.get_role(700896097987723374)
        ve = ch.guild.get_role(700895968652034133)
        hn = ch.guild.get_role(705409643375231036)
        mx = ch.guild.get_role(700896011375214623)
        otros = ch.guild.get_role(700896019134808116)
        pres = ch.guild.get_role(703699073697579019)
        vp = ch.guild.get_role(703698676014383154)
        error_counter = 0

        for member in ch.guild.members:
            if member.bot:
                continue
            tag = await self.config.user(member).tag()
            if tag is None:
                continue
            try:
                player = await self.ofcbsapi.get_player(tag)
                await asyncio.sleep(0.3)
            except brawlstats.errors.RequestError as e:
                error_counter += 1
                if error_counter == 20:
                    await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                      description=f"Stopping after 20 request errors! Displaying the last one:\n({str(e)})"))
                    break
                await asyncio.sleep(1)
                continue
            except Exception as e:
                return await ch.send(embed=discord.Embed(colour=discord.Colour.red(),
                                                         description=f"**Something went wrong while requesting {tag}!**\n({str(e)})"))

            tags = []
            guilds = await self.config.all_guilds()
            latam = guilds[631888808224489482]
            clubs = latam["clubs"]
            for club in clubs:
                info = clubs[club]
                tagn = "#" + info["tag"]
                tags.append(tagn)

            msg = ""
            player_in_club = "name" in player.raw_data["club"]

            if not player_in_club:
                msg += await self.removeroleifpresent(member, derucula, overlay, cl, co, uy, ve, hn, mx, otros, pres, vp)

            if player_in_club and "LA " not in player.club.name and player.club.tag not in tags:
                msg += await self.removeroleifpresent(member, derucula, overlay, cl, co, uy, ve, hn, mx, otros, pres, vp)

            if player_in_club and "LA " in player.club.name and player.club.tag not in tags:
                msg += await self.removeroleifpresent(member, derucula, cl, co, uy, ve, hn, mx, pres, vp)
                msg += await self.addroleifnotpresent(member, otros, overlay)

            if player_in_club and player.club.tag in tags:
                msg += await self.removeroleifpresent(member, otros)
                msg += await self.addroleifnotpresent(member, overlay)
                if " CL" in player.club.name:
                    msg += await self.addroleifnotpresent(member, cl)
                elif " CO" in player.club.name:
                    msg += await self.addroleifnotpresent(member, co)
                elif " UY" in player.club.name:
                    msg += await self.addroleifnotpresent(member, uy)
                elif " VE" in player.club.name:
                    msg += await self.addroleifnotpresent(member, ve)
                elif " HN" in player.club.name:
                    msg += await self.addroleifnotpresent(member, hn)
                elif " MX" in player.club.name:
                    msg += await self.addroleifnotpresent(member, mx)
                else:
                    msg += await self.addroleifnotpresent(member, derucula)
                try:
                    player_club = await self.ofcbsapi.get_club(player.club.tag)
                    for mem in player_club.members:
                        if mem.tag == player.raw_data['tag']:
                            if mem.role.lower() == 'vicepresident':
                                msg += await self.removeroleifpresent(member, pres)
                                msg += await self.addroleifnotpresent(member, vp)
                            elif mem.role.lower() == 'president':
                                msg += await self.removeroleifpresent(member, vp)
                                msg += await self.addroleifnotpresent(member, pres)
                            else:
                                msg += await self.removeroleifpresent(member, vp, pres)
                            break
                except brawlstats.errors.RequestError:
                    msg += "<:offline:642094554019004416> Couldn't retrieve player's club role."

            if msg != "":
                await ch.send(embed=discord.Embed(colour=discord.Colour.blue(), description=msg, title=str(member)))

    @sortroleslatam.before_loop
    async def before_sortroleslatam(self):
        await asyncio.sleep(5)

    @commands.command()
    @commands.guild_only()
    async def userbytag(self, ctx, tag: str):
        """Find user with a specific tag saved"""
        tag = tag.lower().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        for user in (await self.config.all_users()):
            person = self.bot.get_user(user)
            if person is not None:
                if (await self.config.user(person).tag()) == tag:
                    return await ctx.send(f"This tag belongs to **{str(person)}**.")
        await ctx.send("This tag is either not saved or invalid.")

    @commands.command()
    @commands.guild_only()
    async def usersbyclub(self, ctx, tag: str):
        """Find users, who have tag saved, in a specified club"""
        tag = tag.upper().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        msg = ""
        count = 0
        club = await self.ofcbsapi.get_club(tag)
        for user in (await self.config.all_users()):
            person = self.bot.get_user(user)
            if person is not None:
                persontag = await self.config.user(person).tag()
                persontag = "#" + persontag.upper()
                for member in club.members:
                    if member.tag == persontag:
                        msg += f"Tag: **{str(person)}**; IGN: **{member.name}**\n"
                        count = count + 1

        if msg == "":
            await ctx.send(embed=discord.Embed(description="This tag is either invalid or no people from this club saved their tags.", colour=discord.Colour.red()))
        else:
            await ctx.send(embed=discord.Embed(title=f"Total: {count}", description=msg, colour=discord.Colour.blue()))

    @commands.command(aliases=['vpsbyclub'])
    @commands.guild_only()
    async def vpbyclub(self, ctx, tag: str):
        """Find vicepresidents, who have tag saved, in a specified club"""
        tag = tag.upper().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        msg = ""
        count = 0
        club = await self.ofcbsapi.get_club(tag)
        for user in (await self.config.all_users()):
            person = self.bot.get_user(user)
            if person is not None:
                persontag = await self.config.user(person).tag()
                persontag = "#" + persontag.upper()
                for member in club.members:
                    if member.tag == persontag and member.role.lower() == "vicepresident":
                        msg += f"Tag: **{str(person)}**; IGN: **{member.name}**\n"
                        count = count + 1

        if msg == "":
            await ctx.send(embed=discord.Embed(
                description="This tag is either invalid or no people from this club saved their tags.", colour=discord.Colour.red()))
        else:
            await ctx.send(embed=discord.Embed(title=f"Total: {count}", description=msg, colour=discord.Colour.blue()))

    @commands.command()
    @commands.guild_only()
    async def presbyclub(self, ctx, tag: str):
        """Find a club president, who have tag saved, in a specified club"""
        tag = tag.upper().replace('O', '0')
        if tag.startswith("#"):
            tag = tag.strip('#')

        msg = ""
        count = 0
        club = await self.ofcbsapi.get_club(tag)
        for user in (await self.config.all_users()):
            person = self.bot.get_user(user)
            if person is not None:
                persontag = await self.config.user(person).tag()
                persontag = "#" + persontag.upper()
                for member in club.members:
                    if member.tag == persontag and member.role.lower() == "president":
                        msg += f"Tag: **{str(person)}**; IGN: **{member.name}**\n"
                        count = count + 1

        if msg == "":
            await ctx.send(embed=discord.Embed(
                description="This tag is either invalid or no people from this club saved their tags.", colour=discord.Colour.red()))
        else:
            await ctx.send(embed=discord.Embed(title=f"Total: {count}", description=msg, colour=discord.Colour.blue()))

    @commands.command()
    @commands.guild_only()
    async def membersBS(self, ctx, *, rolename):
        role = None
        for r in ctx.guild.roles:
            if r.name.lower() == rolename.lower():
                role = r
                continue
            elif r.name.lower().startswith(rolename.lower()):
                role = r
                continue
        if role is None:
            await ctx.send("No such role in the server.")
            return
        result = role.members
        if not result:
            await ctx.send("No members with such role in the server.")
            return
        discordn = ""
        ign = ""
        clubn = ""
        discords = []
        igns = []
        clubs = []
        for member in result:
            tag = await self.config.user(member).tag()
            if tag is not None:
                player = await self.ofcbsapi.get_player(tag)
                player_in_club = "name" in player.raw_data["club"]
            if len(discordn) > 666 or len(ign) > 666 or len(clubn) > 666:
                discords.append(discordn)
                discordn = ""
                igns.append(ign)
                ign = ""
                clubs.append(clubn)
                clubn = ""
            if tag is None:
                discordn += f"{str(member)}\n"
                ign += "None\n"
                clubn += "None\n"
            elif player_in_club:
                club = await self.ofcbsapi.get_club(player.club.tag)
                for mem in club.members:
                    if mem.tag == player.tag:
                        discordn += f"{str(member)}\n"
                        ign += f"{player.name}\n"
                        clubn += f"{player.club.name}({mem.role.capitalize()})\n"
            elif not player_in_club:
                discordn += f"{str(member)}\n"
                ign += f"{player.name}\n"
                clubn += "None\n"
            await asyncio.sleep(0.1)
        if len(discordn) > 0 or len(ign) > 0 or len(clubn) > 0:
            discords.append(discordn)
            igns.append(ign)
            clubs.append(clubn)
        i = 0
        while i < len(discords):
            embed = discord.Embed(color=discord.Colour.green(), title=f"Members: {str(len(result))}\n")
            embed.add_field(name="Discord", value=discords[i], inline=True)
            embed.add_field(name="IGN", value=igns[i], inline=True)
            embed.add_field(name="Club(Role)", value=clubs[i], inline=True)
            await ctx.send(embed=embed)
            i = i + 1

    @commands.cooldown(1, 20, commands.BucketType.user)
    @commands.command()
    @commands.guild_only()
    async def whitelistclubs(self, ctx):
        """Utility command for whitelist in LA Gaming - Brawl Stars"""
        if ctx.guild.id != 401883208511389716:
            return await ctx.send("This command can only be used in LA Gaming - Brawl Stars.")

        await ctx.trigger_typing()

        whitelist = ctx.guild.get_role(693659561747546142)

        messages = []
        msg = ""
        for member in ctx.guild.members:
            if whitelist not in member.roles:
                continue
            tag = await self.config.user(member).tag()
            alt = await self.config.user(member).alt()
            if tag is None:
                msg += f"**{member.name}**: has no tag saved.\n"
            try:
                player = await self.ofcbsapi.get_player(tag)
                if alt is not None:
                    playeralt = await self.ofcbsapi.get_player(alt)
                await asyncio.sleep(0.2)
            except brawlstats.errors.RequestError as e:
                msg += f"**{member.name}**: request error.\n"
                continue
            except Exception as e:
                msg += "Something went wrong."
                return
            player_in_club = "name" in player.raw_data["club"]
            if alt is not None:
                player_in_club2 = "name" in playeralt.raw_data["club"]
            if len(msg) > 1900:
                messages.append(msg)
                msg = ""
            if player_in_club:
                clubobj = await self.ofcbsapi.get_club(player.club.tag)
                msg += f"**{str(member)}** `{player.trophies}` <:bstrophy:552558722770141204>: {player.club.name} ({len(clubobj.members)}/100)\n"
            else:
                msg += f"**{str(member)}** `{player.trophies}` <:bstrophy:552558722770141204>: not in a club.\n"
            if alt is not None:
                if player_in_club2:
                    clubobj = await self.ofcbsapi.get_club(playeralt.club.tag)
                    msg += f"**{str(member)}'s alt** `{playeralt.trophies}` <:bstrophy:552558722770141204>: {playeralt.club.name} ({len(clubobj.members)}/100)\n"
                else:
                    msg += f"**{str(member)}'s alt** `{playeralt.trophies}` <:bstrophy:552558722770141204>: not in a club.\n"
        if len(msg) > 0:
            messages.append(msg)
        for m in messages:
            await ctx.send(embed=discord.Embed(colour=discord.Colour.green(), description=m))
