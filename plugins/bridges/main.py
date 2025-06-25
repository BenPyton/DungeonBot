# Copyright (c) 2025 Benoît Pelletier
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import asyncio
import aiosqlite
import discord
from discord.ext import commands
from dismob import log
from dismob.event import BotEvents
from plugins.welcome.main import Welcome
from plugins.levels.main import LevelSystem

@discord.app_commands.guild_only()
@discord.app_commands.default_permissions(manage_guild=True)
class Bridges(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.welcome_cog: Welcome = None
        self.level_system_cog: LevelSystem = None
        self.db_path = "db/bridges.db"
        BotEvents.on_ready.register(self.on_ready)
        self.bot.loop.create_task(self.init_db())

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS greeting_xp (
                    guild_id INTEGER PRIMARY KEY,
                    xp_gain INTEGER DEFAULT 35
                )
            """)
            await db.commit()

    @discord.app_commands.command(name="set-greeting-xp", description="Set the XP gain per greeting for this server")
    @discord.app_commands.describe(xp="The amount of XP to award per greeting")
    async def set_greeting_xp(self, interaction: discord.Interaction, xp: int):
        """Set the XP gain per greeting for this guild."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO greeting_xp (guild_id, xp_gain) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET xp_gain = ?",
                (interaction.guild.id, xp, xp)
            )
            await db.commit()
        await interaction.response.send_message(f"Greeting XP gain set to {xp} for this server.", ephemeral=True)

    async def get_greeting_xp(self, guild_id: int) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT xp_gain FROM greeting_xp WHERE guild_id = ?", (guild_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    def on_ready(self, bot: commands.Bot) -> None:
        BotEvents.on_ready.unregister(self.on_ready)
        log.info("Bot is ready, checking cogs...")
        self.welcome_cog = bot.get_cog('Welcome')
        self.level_system_cog = bot.get_cog('LevelSystem')

        if not self.welcome_cog or not self.level_system_cog:
            log.error("Required cogs not found")
            return

        self.welcome_cog.on_greeting.register(self.on_greeting)

    async def cog_unload(self):
        if self.welcome_cog:
            self.welcome_cog.on_greeting.unregister(self.on_greeting)

    def on_greeting(self, interaction: discord.Interaction, greeted_member: discord.Member) -> None:
        log.info(f"Greeting event triggered for {interaction.user} greeting {greeted_member}")
        asyncio.create_task(self.greeting_task(interaction, greeted_member))

    async def greeting_task(self, interaction: discord.Interaction, greeted_member: discord.Member) -> None:
        log.info("Processing greeting...")
        if not self.level_system_cog:
            log.error("LevelSystem cog not available")
            return
        xp_gain = await self.get_greeting_xp(interaction.guild.id)
        if xp_gain <= 0:
            return
        old_level, new_level, exp_gain = await self.level_system_cog.update_user_exp(
            interaction.user, xp_gain, LevelSystem.ExpGainType.WELCOME
        )
        log.info(f"{interaction.user} gained {exp_gain} experience points, old level: {old_level}, new level: {new_level}")
        await log.safe_followup(
            interaction,
            f"You greeted {greeted_member.mention}! You have been awarded {xp_gain} experience points.",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    log.info("Module `bridges` setup")
    await bot.add_cog(Bridges(bot))

async def teardown(bot: commands.Bot):
    log.info("Module `bridges` teardown")
    await bot.remove_cog("Bridges")
