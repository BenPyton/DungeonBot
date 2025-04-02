# Copyright (c) 2025 Benoît Pelletier
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import log
import filehelper
import predicate

load_dotenv()
TOKEN: str = os.getenv('BOT_TOKEN')

config = filehelper.openConfig()

if not config.get("modules"):
    config["modules"] = list()

if not config.get("prefix"):
    config["prefix"] = "/"

prefix = config["prefix"]

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready() -> None:
    log.info(f"Discord.py version: `{discord.__version__}`")
    log.info(f"Logged in as `{bot.user}`")
    for module in config["modules"]:
        try:
            await bot.load_extension(f"plugins.{module}.main")
            log.info(f"Module `{module}` successfully loaded.")
        except Exception as e:
            log.error(f"Failed to load module `{module}`: {e}")

    log.info(f"Bot is ready.")

@bot.command(aliases=["exit"])
@predicate.admin_only()
async def shutdown(ctx: commands.Context) -> None:
    await ctx.message.delete()
    log.info(f"Shutting down bot...")
    await bot.close()

def cleanup() -> None:
    log.info(f"Final cleanup")
    filehelper.saveConfig(config)

@bot.command()
@predicate.admin_only()
async def setPrefix(ctx: commands.Context, new_prefix: str) -> None:
    await ctx.message.delete()
    global prefix
    log.info(f"Setting new command prefix to `{new_prefix}`")

    prefix = new_prefix
    config["prefix"] = new_prefix
    bot.command_prefix = new_prefix

    await log.success(ctx, f"Command prefix successfully set to `{new_prefix}`")
    
####                        ####
#       Module Management      #
####                        ####

@bot.command(aliases=["enable"])
@predicate.admin_only()
async def load(ctx: commands.Context, module: str = None) -> None:
    """
    Load a specific extension module

    Parameters
    ----------
    module : str
        The name of the module to load.
        The entry point of the discord extension will be searched at `plugins/<module name>/main.py`
    """

    await ctx.message.delete()

    if not module:
        await log.failure(ctx, f"Command incorrectly used.\n> Usage: `{prefix}load <module>`")
        return

    try:
        await bot.load_extension(f"plugins.{module}.main")
        config["modules"].append(module)
        await log.success(ctx, f"Module `{module}` successfully loaded.")
    except Exception as e:
        await log.failure(ctx, f"Failed to load module `{module}`: `{e}`")

@bot.command(aliases=["disable"])
@predicate.admin_only()
async def unload(ctx: commands.Context, module: str) -> None:
    """
    Unload a specific extension module

    Parameters
    ----------
    module : str
        The name of the module to unload.
        The entry point of the discord extension will be searched at `plugins/<module name>/main.py`
    """

    await ctx.message.delete()

    if not module:
        await log.failure(ctx, f"Command incorrectly used.\n> Usage: `{prefix}unload <module>`")
        return

    try:
        await bot.unload_extension(f"plugins.{module}.main")
        config["modules"].remove(module)
        await log.success(ctx, f"Module `{module}` successfully unloaded.")
    except Exception as e:
        await log.failure(ctx, f"Failed to unload module `{module}`: `{e}`")

@bot.command(aliases=["rl"])
@predicate.admin_only()
async def reload(ctx: commands.Context, module: str = None) -> None:
    """
    Reload a specific extension module

    Parameters
    ----------
    module : str
        The name of the module to reload.
        The entry point of the discord extension will be searched at `plugins/<module name>/main.py`
    """

    await ctx.message.delete()

    if not module:
        await log.error(ctx, f"Command incorrectly used.\n> Usage: `{prefix}reload <module>`")
        return

    try:
        await bot.reload_extension(f"plugins.{module}.main")
        await log.success(ctx, f"Module `{module}` successfully reloaded.")
    except Exception as e:
        await log.failure(ctx, f"Failed to reload module `{module}`: `{e}`")

@bot.command()
@predicate.admin_only()
async def status(ctx: commands.Context, *args) -> None:
    """
    Display the current status of each named extension module, or display all active modules if no name provided

    Parameters
    ----------
    args : [str, ...] (optional)
        The name of the module to display the status.
        If not provided, will display all active modules instead.
        The entry point of the discord extension will be searched at `plugins/<module name>/main.py`
    """

    await ctx.message.delete()

    if len(args) <= 0:
        loaded_modules: str = f"All active modules ({len(bot.extensions)}):\n"
        for key in bot.extensions:
            loaded_modules += f"- {key}\n"
        await ctx.send(loaded_modules, delete_after=10)

    elif len(args) == 1:
        is_loadded = bot.extensions.get(f"plugins.{args[0]}.main")
        await ctx.send(f"`{args[0]}` module status: {'active :white_check_mark:' if is_loadded else 'inactive :x:'}", delete_after=10)

    else:
        module_status: str = f"Modules status:\n"
        for arg in args:
            is_loadded = bot.extensions.get(f"plugins.{arg}.main")
            module_status += f"- `{arg}` module status: {'active :white_check_mark:' if is_loadded else 'inactive :x:'}\n"
        await ctx.send(module_status, delete_after=10)

# Start the bot and loop until it is shutdown.
bot.run(TOKEN)

# Do any potential cleanup after the bot stopped.
cleanup()
