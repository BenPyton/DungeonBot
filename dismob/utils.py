# Copyright (c) 2025 Benoît Pelletier
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import (Type)
import discord
from dismob import log

async def clear_views(bot: discord.Client, view_types: Type[discord.ui.View] | tuple[Type[discord.ui.View]] | None):
    """Clear all persistent views from the bot"""
    if view_types is None:
        log.warning("No view types provided to clear_views; skipping.")
        return

    views_to_remove: list[discord.ui.View] = []
    for view in bot.persistent_views:
        if isinstance(view, view_types):
            views_to_remove.append(view)
            
    for view in views_to_remove:
        bot.persistent_views.remove(view)

    log.info(f"Removed {len(views_to_remove)} persistent views of types {view_types}")
