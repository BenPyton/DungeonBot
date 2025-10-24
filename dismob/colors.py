# Copyright (c) 2025 Benoît Pelletier
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import discord
from dismob import log

# List of known discord.py color names
known_colors: set[str] = {
    'teal', 'dark_teal', 'brand_green', 'green', 'dark_green',
    'blue', 'dark_blue', 'purple', 'dark_purple', 'magenta',
    'dark_magenta', 'gold', 'dark_gold', 'orange', 'dark_orange',
    'brand_red', 'red', 'dark_red', 'lighter_grey', 'lighter_gray',
    'dark_grey', 'dark_gray', 'light_grey', 'light_gray', 'darker_grey',
    'darker_gray', 'og_blurple', 'blurple', 'greyple', 'dark_theme',
    'fuchsia', 'yellow', 'dark_embed', 'light_embed', 'pink', 'dark_pink'
}

def str_to_color(color_str: str) -> discord.Colour:
    color_str = color_str.strip()

    # try named color
    color_name = color_str.lower()
    if color_name in known_colors:
        func = getattr(discord.Colour, color_name)
        return func()
    
    # try hex code
    try:
        if color_str.startswith("#"):
            color_str = color_str[1:]
        if len(color_str) == 3:
            # Expand 3-char hex to 6-char (e.g., "fff" -> "ffffff")
            color_str = ''.join([c*2 for c in color_str])
        if len(color_str) == 6:
            return discord.Colour(int(color_str, 16))
    except Exception:
        pass

    log.warning(f"Invalid color string '{color_str}', using default color (blurple).")
    return discord.Colour.blurple()
