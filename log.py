# Copyright (c) 2025 Benoît Pelletier
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import datetime
from discord.ext import commands
from colorama import Fore, Style

###   Send messages to the client   ###

async def client(ctx: commands.Context, msg: str, delete_after: int = 5):
    return await ctx.send(msg, delete_after=delete_after)

async def success(ctx: commands.Context, msg: str, delete_after: int = 5):
    return await client(ctx, f":white_check_mark: {msg}", delete_after=delete_after)
    
async def failure(ctx: commands.Context, msg: str, delete_after: int = 5):
    return await client(ctx, f":x: {msg}", delete_after=delete_after)

###   Print in the standard output   ###

def log(msg: str) -> None:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Style.BRIGHT}{Fore.LIGHTBLACK_EX}{now} {Style.RESET_ALL}{msg}")

def info(msg: str) -> None:
    log(f"{Style.BRIGHT}{Fore.BLUE}INFO     {Style.RESET_ALL}{msg}")

def warning(msg: str) -> None:
    log(f"{Style.BRIGHT}{Fore.YELLOW}WARNING  {Style.RESET_ALL}{msg}")

def error(msg: str) -> None:
    log(f"{Style.BRIGHT}{Fore.RED}ERROR    {Style.RESET_ALL}{msg}")
