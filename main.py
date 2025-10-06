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
HEROES = ["Chenko", "Amadeus", "Yeonwoo", "Amane", "Howard", "Quinn", "Gordon", "Fahd", "Saul", "Hilde", "Eric", "Jabel"]

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
    "Eric": 110,
    "Jabel": 111
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
    },
    "Jabel": {
        "No Skill": {"effect": "No bonus", "values": [0]},
        "Rally Flag": {"effect": "Damage Taken Chance Down", "values": [8, 16, 24, 32, 40]},
        "Hero's Domain": {"effect": "Damage Up", "values": [10, 20, 30, 40, 50]},
        "Youthful Rage": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]}
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
        description="Configure your Bear Hunt rally team for maximum effectiveness!\n\n**Features:**\n⚔️ 12 unique heroes with expedition skills\n👑 **Rally Captain**: Choose from all expedition skills\n🤝 **Rally Joiners**: Automatically use first expedition skill only\n🔄 Multiplicative bonuses for hero diversity\n📊 Color-coded optimization results\n🎯 Support for duplicate heroes",
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
            description=f"**Rally Captain:** {self.captain}\n\nSelect your expedition skill:",
            color=0x0099ff
        )
        
        # Switch to skill configuration for captain
        skill_view = CaptainSkillConfigView(self.captain)
        await interaction.response.edit_message(embed=embed, view=skill_view)

class CaptainSkillConfigView(ui.View):
    def __init__(self, captain):
        super().__init__(timeout=300)
        self.captain = captain
        self.selected_skill = None
        self.selected_effect = None
        
        # Add skill selection dropdown for captain (can choose from all skills)
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
        joiner_select.callback = lambda inter: self.joiner_count_callback(inter, effect_value)
        self.add_item(joiner_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def joiner_count_callback(self, interaction: Interaction, captain_effect):
        joiner_count = int(interaction.data['values'][0])
        
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Configuration",
            description=f"**Rally Captain:** {self.captain} ✅\n**Joiners to configure:** {joiner_count}\n\nLet's configure each joiner hero...",
            color=0x0099ff
        )
        
        # Switch to joiner configuration
        joiner_view = JoinerConfigView(self.captain, captain_effect, joiner_count)
        await interaction.response.edit_message(embed=embed, view=joiner_view)

# Joiner Configuration Class
class JoinerConfigView(ui.View):
    def __init__(self, captain, captain_effect, joiner_count):
        super().__init__(timeout=300)
        self.captain = captain
        self.captain_effect = captain_effect
        self.joiner_count = joiner_count
        self.joiners = []
        self.current_joiner = 0
        
        # Start with first joiner selection
        self.show_joiner_selection()
    
    def show_joiner_selection(self):
        self.clear_items()
        
        # Add hero selection for current joiner
        hero_options = []
        for hero in HEROES:
            hero_options.append(discord.SelectOption(
                label=hero,
                value=hero,
                description=f"Select {hero} as joiner #{self.current_joiner + 1}"
            ))
        
        hero_select = ui.Select(
            placeholder=f"Choose joiner hero #{self.current_joiner + 1}...",
            options=hero_options
        )
        hero_select.callback = self.joiner_hero_callback
        self.add_item(hero_select)
    
    async def joiner_hero_callback(self, interaction: Interaction):
        selected_hero = interaction.data['values'][0]
        
        # Get the only expedition skill for this hero
        skill_name = list(HERO_SKILLS[selected_hero].keys())[0]
        skill_data = HERO_SKILLS[selected_hero][skill_name]
        
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Configuration",
            description=f"**Rally Captain:** {self.captain} ✅\n**Current Joiner:** {selected_hero}\n**Expedition Skill:** {skill_name}\n**Effect:** {skill_data['effect']}\n\nSelect skill level:",
            color=0x0099ff
        )
        
        self.clear_items()
        effect_options = []
        for i, value in enumerate(skill_data['values']):
            effect_options.append(discord.SelectOption(
                label=f"Level {i+1}: +{value}%",
                value=f"{selected_hero}|{skill_name}|{value}",
                description=f"{skill_data['effect']} +{value}%"
            ))
        
        effect_select = ui.Select(
            placeholder="Choose skill level...",
            options=effect_options
        )
        effect_select.callback = self.joiner_effect_callback
        self.add_item(effect_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def joiner_effect_callback(self, interaction: Interaction):
        selected = interaction.data['values'][0]
        hero_name, skill_name, effect_value = selected.split('|')
        effect_value = int(effect_value)
        
        # Save this joiner
        self.joiners.append({
            'hero': hero_name,
            'skill': skill_name,
            'effect': effect_value
        })
        
        self.current_joiner += 1
        
        # Check if we need more joiners
        if self.current_joiner < self.joiner_count:
            embed = discord.Embed(
                title="🐻 Bear Hunt Rally Configuration",
                description=f"**Rally Captain:** {self.captain} ✅\n**Joiners Configured:** {self.current_joiner}/{self.joiner_count}\n\n✅ Joiner #{self.current_joiner} configured! Setting up next joiner...",
                color=0x0099ff
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Small delay then show next joiner selection
            import asyncio
            await asyncio.sleep(1)
            
            embed = discord.Embed(
                title="🐻 Bear Hunt Rally Configuration", 
                description=f"**Rally Captain:** {self.captain} ✅\n**Joiners Configured:** {self.current_joiner}/{self.joiner_count}\n\n⚔️ Select joiner #{self.current_joiner + 1} hero:",
                color=0x0099ff
            )
            
            self.show_joiner_selection()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            # All joiners configured, show final summary
            await self.show_final_summary(interaction)
    
    async def show_final_summary(self, interaction: Interaction):
        # Calculate final rally bonus with multiplicative stacking
        all_heroes = [self.captain] + [j['hero'] for j in self.joiners]
        
        summary_lines = [f"**Rally Captain:** {self.captain} (+{self.captain_effect}%)"]
        for i, joiner in enumerate(self.joiners):
            summary_lines.append(f"**Joiner {i+1}:** {joiner['hero']} (+{joiner['effect']}%)")
        
        # Calculate multiplicative bonuses
        bonus_effects = {}
        # Add captain bonus
        captain_op = HERO_EFFECT_OPS[self.captain]
        bonus_effects[captain_op] = self.captain_effect
        
        # Add joiner bonuses
        for joiner in self.joiners:
            joiner_op = HERO_EFFECT_OPS[joiner['hero']]
            if joiner_op in bonus_effects:
                bonus_effects[joiner_op] += joiner['effect']  # Same hero type - additive
            else:
                bonus_effects[joiner_op] = joiner['effect']  # Different hero type
        
        # Calculate final multiplier
        damage_multiplier = 1.0
        for effect_op, bonus in bonus_effects.items():
            damage_multiplier *= (1 + bonus/100)
        
        total_percentage = (damage_multiplier - 1) * 100
        
        if total_percentage < 50:
            color = 0xff0000
            status = "Below Optimal"
        elif total_percentage <= 100:
            color = 0xffa500  
            status = "Good Setup"
        else:
            color = 0x00ff00
            status = "Excellent!"
        
        summary_lines.append(f"\n🎯 **Total Rally Size:** {len(all_heroes)} heroes")
        summary_lines.append(f"📋 **Rally Composition:** {', '.join(all_heroes)}")
        
        embed = discord.Embed(
            title="🧮 Bear Hunt Rally Calculation",
            description="\n".join(summary_lines),
            color=color
        )
        
        embed.add_field(
            name="📊 Total Rally Bonus",
            value=f"**{total_percentage:.1f}%** ({status})",
            inline=False
        )
        
        # Show calculation method
        if len(bonus_effects) == 1:
            embed.add_field(
                name="📈 Calculation Method",
                value="**Simple Addition** (same hero types)",
                inline=False
            )
        else:
            embed.add_field(
                name="📈 Calculation Method", 
                value="**Multiplicative Stacking** (different hero types)",
                inline=False
            )
        
        self.clear_items()
        
        # Add new rally button
        new_rally_btn = ui.Button(
            label="Calculate New Rally", 
            style=discord.ButtonStyle.primary, 
            emoji="🆕"
        )
        new_rally_btn.callback = self.reset_callback
        self.add_item(new_rally_btn)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def reset_callback(self, interaction: Interaction):
        # Start a completely new rally calculation
        new_view = RallyCalculatorView()
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Calculator",
            description="Select your rally captain to begin:",
            color=0x0099ff
        )
        await interaction.response.edit_message(embed=embed, view=new_view)
    
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