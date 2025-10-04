# 🐻 Bear Hunt Rally Calculator Bot

A Discord bot for optimizing Bear Hunt rally compositions with multiplicative bonus calculations.

## Features

- ⚔️ **11 unique heroes** with expedition skills
- 🔄 **Multiplicative bonuses** for hero diversity  
- 📊 **Color-coded results** (Red/Orange/Green)
- 🎯 **Duplicate hero support** for flexible strategies
- 🧮 **Advanced calculations** with detailed breakdowns

## Commands

- `!hello` - Test bot connectivity
- `!rally` - Start the Bear Hunt Rally Calculator

## Deployment on Koyeb

### Prerequisites
1. Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)
2. GitHub account
3. Koyeb account

### Setup Steps

1. **Push to GitHub**
   - Create a new GitHub repository
   - Push these files: `main.py`, `requirements.txt`, `keep_alive.py`

2. **Deploy on Koyeb**
   - Go to [koyeb.com](https://www.koyeb.com)
   - Sign up with GitHub
   - Click "Create App"
   - Connect your GitHub repository
   - Set environment variable: `DISCORD_TOKEN = your_bot_token_here`
   - Set run command: `python3 main.py`
   - Click "Deploy App"

3. **Bot Goes Live**
   - Bot will appear online in Discord within 1-2 minutes
   - Test with `!hello` and `!rally` commands

## Bot Capabilities

### Rally Calculation Types

**Same Hero Types (Additive):**
- 4 identical heroes → Simple addition
- Example: 4×Chenko = 100% bonus

**Mixed Hero Types (Multiplicative):**  
- Different heroes → Multiplicative stacking
- Example: 2×Chenko + 2×Amane = 181% bonus (+81% improvement!)

### Hero Selection
- **Captain + 1-4 Joiners** (minimum 1 joiner required)
- **All 11 heroes available** with unique expedition skills
- **Duplicate heroes allowed** for flexible strategies
- **Individual skill configuration** for each hero

### Results Display
- 🔴 **Red**: <100% (Below Optimal)
- 🟠 **Orange**: 100-110% (Good)
- 🟢 **Green**: >110% (Excellent)

## Technical Details

- Built with `py-cord` for modern Discord interactions
- Environment variable configuration for security
- Flask keep-alive server for 24/7 uptime
- Error handling to prevent crashes
- Multiplicative bonus calculation system

## Support

For issues or questions about the rally calculator mechanics, refer to the Kingshot Formula documentation.