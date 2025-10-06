import os
import discord
from discord.ext import commands
from discord import ui, Interaction

# Optional: Import keep-alive for 24/7 hosting
try:
    from keep_alive import keep_alive
    keep_alive()
except ImportError:
    print("ℹ️ Keep-alive not available (optional)")

# Get bot token from environment variable for secure deployment
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

if not BOT_TOKEN:
    print("❌ Error: DISCORD_TOKEN environment variable not set!")
    exit(1)

# Enhanced bot with Bear Hunt Rally Calculator
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Hero data
HEROES = ["Chenko", "Amadeus", "Yeonwoo", "Amane", "Howard", "Quinn", "Gordon", "Fahd", "Saul", "Hilde", "Eric"]

# Hero effect operation mapping for multiplicative bonuses
HERO_EFFECT_OPS = {
    "Chenko": 101,
    "Amadeus": 102, 
    "Yeonwoo": 103,
    "Amane": 102,  # Same op as Amadeus for multiplicative stacking
    "Howard": 104,
    "Quinn": 105,
    "Gordon": 106,
    "Fahd": 107,
    "Saul": 108,
    "Hilde": 109,
    "Eric": 110
}

HERO_SKILLS = {
    "Chenko": {
        "Stand of Arms": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]},
        "Shield Wall": {"effect": "Damage Taken Down", "values": [4, 8, 12, 16, 20]}
    },
    "Amadeus": {
        "Battle Ready": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]},
        "Way of the Blade": {"effect": "Attack Up", "values": [5, 10, 15, 20, 25]},
        "Unrighteous Strike": {"effect": "Damage Dealt Chance Up", "values": [8, 16, 24, 32, 40]}
    },
    "Yeonwoo": {
        "On Guard": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]},
        "Well-Traveled": {"effect": "Increases Research Speed", "values": [3, 6, 9, 12, 15]}
    },
    "Amane": {
        "Tri-Phalanx": {"effect": "Attack Up", "values": [5, 10, 15, 20, 25]},
        "Exorcism": {"effect": "Healing Speed Up", "values": [10, 20, 30, 40, 50]}
    },
    "Howard": {
        "Defenders' Edge": {"effect": "Damage Taken Down", "values": [4, 8, 12, 16, 20]},
        "Weaken": {"effect": "Enemy Troops Attack Down", "values": [4, 8, 12, 16, 20]}
    },
    "Quinn": {
        "Sixth Sense": {"effect": "Damage Taken Down", "values": [4, 8, 12, 16, 20]},
        "Vigor": {"effect": "Health Up", "values": [5, 10, 15, 20, 25]}
    },
    "Gordon": {
        "Bloodthirsty": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]},
        "Protection": {"effect": "Damage Taken Down", "values": [4, 8, 12, 16, 20]}
    },
    "Fahd": {
        "Hunter": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]},
        "Assassinate": {"effect": "Damage Dealt Chance Up", "values": [8, 16, 24, 32, 40]}
    },
    "Saul": {
        "Blade Dance": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]},
        "Trial by Fire": {"effect": "Damage Taken Chance Down", "values": [8, 16, 24, 32, 40]}
    },
    "Hilde": {
        "Iron Will": {"effect": "Damage Taken Down", "values": [4, 8, 12, 16, 20]},
        "Overwhelm": {"effect": "Enemy Troops Attack Down", "values": [4, 8, 12, 16, 20]}
    },
    "Eric": {
        "Holy Warrior": {"effect": "Enemy Troop Attack Down", "values": [4, 8, 12, 16, 20]},
        "Conviction": {"effect": "Damage Taken Down", "values": [4, 8, 12, 16, 20]},
        "Exhortation": {"effect": "Health Up", "values": [5, 10, 15, 20, 25]}
    }
}

@bot.event
async def on_ready():
    print(f"🤖 {bot.user} has logged in!")
    print("🐻 Bear Hunt Rally Calculator ready for deployment!")

# Super simple test commands
@bot.command()
async def alive(ctx):
    """Super simple alive check"""
    await ctx.send("🟢 Bot is alive!")

@bot.command()
async def test(ctx):
    """Simple test command"""
    await ctx.send("✅ Bot is working! All systems operational. 🚀")

@bot.command()
async def rally(ctx):
    """Start the Bear Hunt Rally Calculator"""
    embed = discord.Embed(
        title="🐻 Bear Hunt Rally Calculator",
        description="Configure your Bear Hunt rally team for maximum effectiveness!\n\n**Features:**\n⚔️ 11 unique heroes with expedition skills\n🔄 Multiplicative bonuses for hero diversity\n📊 Color-coded optimization results\n🎯 Support for duplicate heroes",
        color=0x0099ff
    )
    
    view = RallyCalculatorView()
    await ctx.send(embed=embed, view=view)

# Rally Calculator UI Classes
class RallyCalculatorView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.captain = None
        
        # Add captain selection dropdown
        captain_select = ui.Select(
            placeholder="Choose your rally captain",
            options=[
                discord.SelectOption(
                    label=hero,
                    value=hero,
                    description=f"Select {hero} as rally captain",
                    emoji="👑"
                )
                for hero in HEROES
            ]
        )
        captain_select.callback = self.captain_callback
        self.add_item(captain_select)
    
    async def captain_callback(self, interaction: Interaction):
        self.captain = interaction.data['values'][0]
        
        embed = discord.Embed(
            title=f"🐻 Rally Captain: {self.captain}",
            description=f"**Rally Captain:** {self.captain}\n\nNow use the buttons below to configure skills and joiners.",
            color=0x0099ff
        )
        
        # Switch to skill configuration
        skill_view = SkillConfigView(self.captain)
        await interaction.response.edit_message(embed=embed, view=skill_view)

class SkillConfigView(ui.View):
    def __init__(self, captain):
        super().__init__(timeout=300)
        self.captain = captain
        self.selected_skill = None
        self.selected_effect = None
        
        # Add skill selection dropdown
        skill_options = []
        for skill_name in HERO_SKILLS[captain].keys():
            skill_options.append(discord.SelectOption(
                label=skill_name,
                value=skill_name,
                description=f"{HERO_SKILLS[captain][skill_name]['effect']}"
            ))
        
        skill_select = ui.Select(
            placeholder="Choose expedition skill...",
            options=skill_options
        )
        skill_select.callback = self.skill_callback
        self.add_item(skill_select)
    
    async def skill_callback(self, interaction: Interaction):
        selected_skill = interaction.data['values'][0]
        self.selected_skill = selected_skill
        skill_effects = HERO_SKILLS[self.captain][selected_skill]
        
        embed = discord.Embed(
            title=f"🐻 Rally Captain: {self.captain}",
            description=f"**Rally Captain:** {self.captain}\n**Selected Skill:** {selected_skill}\n**Effect:** {skill_effects['effect']}\n\nNow select the effect level:",
            color=0x0099ff
        )
        
        # Add effect level selection
        self.clear_items()
        effect_options = []
        for i, value in enumerate(skill_effects['values']):
            effect_options.append(discord.SelectOption(
                label=f"Level {i+1}: +{value}%",
                value=f"{selected_skill}|{value}",
                description=f"{skill_effects['effect']} +{value}%"
            ))
        
        effect_select = ui.Select(
            placeholder="Choose effect level...",
            options=effect_options
        )
        effect_select.callback = self.effect_callback
        self.add_item(effect_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def effect_callback(self, interaction: Interaction):
        selected = interaction.data['values'][0]
        skill_name, effect_value = selected.split('|')
        effect_value = int(effect_value)
        self.selected_effect = effect_value
        
        skill_data = HERO_SKILLS[self.captain][skill_name]
        effect_name = skill_data["effect"]
        
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Setup Complete!",
            description=f"**Rally Captain:** {self.captain}\n**Skill:** {skill_name}\n**Effect:** {effect_name} (+{effect_value}%)\n\n✅ Captain ready! Now choose joiner heroes:",
            color=0x00ff00
        )
        
        # Add joiner selection
        self.clear_items()
        joiner_options = []
        for i in range(1, 5):
            joiner_options.append(discord.SelectOption(
                label=f"{i} Joiner Hero{'s' if i > 1 else ''}",
                value=str(i),
                description=f"Add {i} joiner hero{'s' if i > 1 else ''} to the rally"
            ))
        
        joiner_select = ui.Select(
            placeholder="How many joiner heroes? (1-4 required)",
            options=joiner_options
        )
        joiner_select.callback = self.joiner_count_callback
        self.add_item(joiner_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def joiner_count_callback(self, interaction: Interaction):
        joiner_count = int(interaction.data['values'][0])
        captain_bonus = self.selected_effect
        
        # Calculate basic rally bonus
        total_bonus = captain_bonus + 100  # Base 100% + captain skill
        
        if total_bonus < 125:
            color = 0xff0000
            status = "Below Optimal"
        elif total_bonus <= 150:
            color = 0xffa500
            status = "Good Setup"
        else:
            color = 0x00ff00
            status = "Excellent!"
        
        embed = discord.Embed(
            title="🧮 Bear Hunt Rally Calculation",
            description=f"**Rally Captain:** {self.captain} (+{captain_bonus}%)",
            color=color
        )
        
        embed.add_field(name="📊 Total Rally Bonus", value=f"**{total_bonus}%** ({status})", inline=False)
        embed.add_field(name="🎯 Joiners", value=f"{joiner_count} heroes selected", inline=False)
        
        # Add new rally button
        self.clear_items()
        new_rally_btn = ui.Button(label="Calculate New Rally", style=discord.ButtonStyle.primary, emoji="🆕")
        new_rally_btn.callback = self.reset_callback
        self.add_item(new_rally_btn)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def reset_callback(self, interaction: Interaction):
        new_view = RallyCalculatorView()
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Calculator",
            description="Select your rally captain to begin:",
            color=0x0099ff
        )
        await interaction.response.edit_message(embed=embed, view=new_view)

if __name__ == "__main__":
    print("🚀 Starting Bear Hunt Rally Calculator for deployment...")
    bot.run(BOT_TOKEN)