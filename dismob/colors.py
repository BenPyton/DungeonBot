# Copyright (c) 2025 Benoît Pelletier
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import discord
from dismob import log

def str_to_color(color_str: str) -> discord.Colour:
    color_str = color_str.strip()

    # try named color
    func = getattr(discord.Colour, color_str.lower(), None)
    if callable(func):
        return func()
    
    # try hex code
    try:
        if color_str.startswith("#"):
            color_str = color_str[1:]
        if len(color_str) == 6:
            return discord.Colour(int(color_str, 16))
    except Exception:
        pass

    log.warning(f"Invalid color string '{color_str}', trying named color fallback.")
    return discord.Colour.blurple()
