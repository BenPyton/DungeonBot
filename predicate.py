# Copyright (c) 2025 Benoît Pelletier
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from discord.ext import commands

def is_owner():
    async def pred(ctx: commands.Context):
        if ctx.guild is None:
            return False
        return ctx.guild.owner_id == ctx.author.id
    return commands.check(pred)


def admin_only():
    return commands.check_any(is_owner(), commands.has_permissions(administrator=True))
