# Discord UI Test Bot

A simple Discord bot that demonstrates dropdown menus and button interactions.

## Features

- Slash command `/test` that shows a dropdown menu
- Two selectable options in the dropdown
- Apply and Cancel buttons
- Interactive responses with embeds

## Setup Instructions

1. **Create a Discord Application:**
   - Go to https://discord.com/developers/applications
   - Click "New Application" and give it a name
   - Go to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token

2. **Configure the Bot:**
   - Open `config.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token

3. **Invite the Bot to Your Server:**
   - In the Discord Developer Portal, go to OAuth2 > URL Generator
   - Select "bot" and "applications.commands" scopes
   - Select necessary permissions (Send Messages, Use Slash Commands, etc.)
   - Use the generated URL to invite the bot to your server

4. **Run the Bot:**
   ```
   python bot.py
   ```

## Usage

Once the bot is running and invited to your server:

1. Type `/test` in any channel
2. Select an option from the dropdown menu
3. Click "Apply" to confirm or "Cancel" to cancel
4. The bot will respond with a confirmation message

## Files

- `bot.py` - Main bot code
- `config.py` - Configuration file for the bot token
- `README.md` - This file

## Dependencies

- py-cord (already installed)

## Notes

- The bot uses slash commands which may take a few minutes to register
- Make sure the bot has the necessary permissions in your Discord server