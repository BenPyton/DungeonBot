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
from helpcommand import MyHelpCommand

load_dotenv()
TOKEN: str = os.getenv('BOT_TOKEN')

config = filehelper.openConfig()

if not config.get("modules"):
    config["modules"] = list()

if not config.get("prefix"):
    config["prefix"] = "/"

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=config["prefix"], intents=intents, help_command=MyHelpCommand())

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

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CheckFailure):
        # Handle check failures (e.g., user doesn't meet the requirements)
        await log.failure(interaction, "You do not have permission to use this command.")
    elif isinstance(error, discord.app_commands.CommandNotFound):
        # Handle unknown commands
        await log.failure(interaction, "This command does not exist.")
    else:
        # Handle other errors
        await log.failure(interaction, "An unexpected error occurred while executing the command.")

@bot.tree.command(description="Shutdown gracefully the bot")
@predicate.app_is_bot_owner()
async def shutdown(interaction: discord.Interaction) -> None:
    log.info("Shutting down bot...")
    await log.client(interaction, "Shutting down bot...")
    await bot.close()
    log.info("Bot has been shut off.")


def cleanup() -> None:
    log.info(f"Final cleanup")
    filehelper.saveConfig(config)

@bot.tree.command(description="Change the prefix for the bot's commands")
@predicate.app_is_bot_owner()
async def setprefix(interaction: discord.Interaction, new_prefix: str) -> None:
    global prefix
    log.info(f"Setting new command prefix to `{new_prefix}`")

    prefix = new_prefix
    config["prefix"] = new_prefix
    bot.command_prefix = new_prefix

    await log.success(interaction, f"Command prefix successfully set to `{new_prefix}`")

@bot.hybrid_command(description="Sync the slash commands added/removed by modules")
@predicate.bot_is_bot_owner()
async def sync(ctx: commands.Context | discord.Interaction) -> None:
    if isinstance(ctx, commands.Context):
        await ctx.message.delete()
    global prefix
    log.info("Syncing slash commands")
    await bot.tree.sync()
    await log.success(ctx, "Slash commands synced successfully!\n*It may take some times to propagate to all guilds...*")
    
####                        ####
#       Module Management      #
####                        ####

def getAllModules() -> list[str]:
    """
    Get all available modules in the `plugins` directory
    """
    available_modules: list[str] = []
    for dir in os.listdir("plugins"):
        available_modules.append(dir)
    return available_modules

def isModuleActive(module: str) -> bool:
    return True if bot.extensions.get(f"plugins.{module}.main") else False

def getModuleStatus(module: str) -> str:
    return "active :white_check_mark:" if isModuleActive(module) else "inactive :x:"

@bot.tree.command(description="Manage modules of the bot (list/status/load/unload/reload)")
@discord.app_commands.describe(command="The command to use on the bot's modules.")
@discord.app_commands.choices(command=[
    discord.app_commands.Choice(name="list", value="list"),
    discord.app_commands.Choice(name="status", value="status"),
    discord.app_commands.Choice(name="load", value="load"),
    discord.app_commands.Choice(name="unload", value="unload"),
    discord.app_commands.Choice(name="reload", value="reload"),
    ])
@predicate.app_is_bot_owner()
async def modules(interaction: discord.Interaction, command: str, args: str = None) -> None:
    args_list: list[str] = args.split(' ') if args else list()
    
    log.info(f"User `{interaction.user.name}` used command `{command}` with args {args_list} in guild `{interaction.guild.name}`")

    if command == "list":
        await log.client(interaction, listModules())
    elif command == "status":
        await log.client(interaction, modulesStatus(args_list))
    elif command == "load":
        result: tuple[bool, str] = await loadModules(args_list)
        if not result[0]:
            await log.failure(interaction, result[1])
        else:
            await log.client(interaction, result[1])
    elif command == "unload":
        result: tuple[bool, str] = await unloadModules(args_list)
        if not result[0]:
            await log.failure(interaction, result[1])
        else:
            await log.client(interaction, result[1])
    elif command == "reload":
        result: tuple[bool, str] = await reloadModules(args_list)
        if not result[0]:
            await log.failure(interaction, result[1])
        else:
            await log.client(interaction, result[1])
    else:
        await log.failure(interaction, f"Unsupported command: `{command}`")

def listModules() -> str:
    """
    List all available modules in the `plugins` directory
    """
    allModules: list[str] = getAllModules()
    count: int = len(allModules)
    available_modules: str = f"There are {count if count > 0 else 'no'} available module{'s' if count > 1 else ''}:\n"
    for i, dir in enumerate(allModules):
        available_modules += f"{dir}{', ' if i < count - 1 else ''}"
    return available_modules

def modulesStatus(args: list[str]) -> str:
    if len(args) <= 0:
        allModules: list[str] = getAllModules()
        result: str = f"All modules ({len(allModules)}):\n"
        for mod in allModules:
            result += f"- `{mod}` (status: {getModuleStatus(mod)})\n"
        return result

    elif len(args) == 1:
        return f"`{args[0]}` module status: {getModuleStatus(args[0])}"

    else:
        module_status: str = f"Modules status:\n"
        for arg in args:
            module_status += f"- `{arg}` module status: {getModuleStatus(arg)}\n"
        return module_status

async def loadModules(args: list[str]) -> tuple[bool, str]:
    if len(args) <= 0:
        return False, "You must provide at least one module name to load."

    result = ""
    for arg in args:
        try:
            await bot.load_extension(f"plugins.{arg}.main")
            config["modules"].append(arg)
            result += f":white_check_mark: Module `{arg}` successfully loaded.\n"
        except commands.errors.ExtensionAlreadyLoaded:
            result += f":white_check_mark: Module `{arg}` is already loaded\n"
        except commands.errors.ExtensionNotFound:
            result += f":x: Module `{arg}` does not exists\n"
        except Exception as e:
            result += f":x: Failed to load module `{arg}`: `{e}`\n"
    return True, result

async def unloadModules(args: list[str]) -> tuple[bool, str]:
    if len(args) <= 0:
        return False, "You must provide at least one module name to unload."

    result = ""
    for arg in args:
        try:
            await bot.unload_extension(f"plugins.{arg}.main")
            config["modules"].remove(arg)
            result += f":white_check_mark: Module `{arg}` successfully unloaded.\n"
        except commands.errors.ExtensionNotLoaded:
            result += f":white_check_mark: Module `{arg}` is already unloaded\n"
        except commands.errors.ExtensionNotFound:
            result += f":x: Module `{arg}` does not exists\n"
        except Exception as e:
            result += f":x: Failed to unload module `{arg}`: `{e}`\n"
    return True, result

async def reloadModules(args: list[str]) -> tuple[bool, str]:
    if len(args) <= 0:
        return False, "You must provide at least one module name to reload."

    result = ""
    for arg in args:
        try:
            await bot.reload_extension(f"plugins.{arg}.main")
            result += f":white_check_mark: Module `{arg}` successfully reloaded.\n"
        except commands.errors.ExtensionNotLoaded:
            result += f":x: Module `{arg}` is not loaded\n"
        except commands.errors.ExtensionNotFound:
            result += f":x: Module `{arg}` does not exists\n"
        except Exception as e:
            result += f":x: Failed to reload module `{arg}`: `{e}`\n"
    return True, result

# Start the bot and loop until it is shutdown.
bot.run(TOKEN)

# Do any potential cleanup after the bot stopped.
cleanup()
