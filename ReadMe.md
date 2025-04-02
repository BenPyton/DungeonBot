# Discord Modular Bot (Dismob)

This is a base discord modular bot using discord.py

Every features must be done in bot extensions placed in `plugins/<module>/main.py`.

An example extension `ping` is available which adds only one command `ping` to the bot.

## Installation

Make sure you've installed python.

Add a `.env` file at the root directory (alongside `main.py`) and add those lines:

```txt
BOT_TOKEN="your bot token here"
CONFIG_DIR="config"
```

> [!NOTE]
> The `CONFIG_DIR` is optional and will default to `config` if not set.

Run this command:

```cmd
py -3 -m pip install requirements. txt
```

> [!NOTE]
> The `py -3` at the start is used to differentiate multiple versions of python installed on your computer.

Then to start the bot run:

```cmd
py -3 main.py
```

## Commands

There are some core commands built into the bot itself, they help manage the modules and other crucial features.  
All of them are only available to the administrators.

Command | Aliases | Description
--- | --- | ---
`shutdown` | | Stop the bot.
`setPrefix <prefix>` | | Set the command prefix of the bot.
`load <module>` | `enable` `activate`| Load a specific module. For example `load ping` will load the `plugins/ping/main.py` extension.
`unload <module>` | `disable` `deactivate` | Unload a specific module. For example `load ping` will unload the `plugins/ping/main.py` extension.
`reload <module>` | `rl` | Reload a specific module. For example `load ping` will reload the `plugins/ping/main.py` extension.
`status [<module> ...]` | | Display the loaded status of the named modules. If no name is provided, list all loaded modules.
