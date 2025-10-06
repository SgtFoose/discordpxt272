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

# Hero data - Jabel included (captain can use, joiners should avoid chance-based skills)
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
        description="Configure your Bear Hunt rally team for maximum effectiveness!\n\n**Rally Mechanics (Official Guide):**\n👑 **Rally Captain**: Select 1-3 heroes (up to 9 skills total)\n🤝 **Rally Members**: Contribute 4 highest-level first expedition skills\n📊 **Captain skills**: All additive within rally\n⚠️ **Note**: Chance-based skills (like Jabel) don't stack\n🔄 Multiplicative bonuses for hero diversity\n📊 Color-coded optimization results",
        color=0x0099ff
    )
    
    view = RallyCalculatorView()
    await ctx.send(embed=embed, view=view)

# Rally Calculator UI Classes
class RallyCalculatorView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        
        # Add simple button to start with default captain name
        start_button = ui.Button(
            label="Start Rally Setup",
            style=discord.ButtonStyle.primary,
            emoji="⚔️"
        )
        start_button.callback = self.start_setup_callback
        self.add_item(start_button)
    
    async def start_setup_callback(self, interaction: Interaction):
        # Use the Discord username as captain name
        captain_name = interaction.user.display_name
        
        embed = discord.Embed(
            title=f"🐻 Rally Captain Setup",
            description=f"**Rally Captain:** {captain_name}\\n\\nAs Rally Captain, you can select 1-3 heroes for your squad.\\n**How many heroes do you want to bring?**",
            color=0x0099ff
        )
        
        # Switch to hero count selection
        hero_count_view = HeroCountView(captain_name)
        await interaction.response.edit_message(embed=embed, view=hero_count_view)

class HeroCountView(ui.View):
    def __init__(self, captain_name):
        super().__init__(timeout=300)
        self.captain_name = captain_name
        
        # Add hero count selection (1-3)
        hero_count_options = [
            discord.SelectOption(label="1 Hero", value="1", description="Bring 1 hero (up to 3 skills)"),
            discord.SelectOption(label="2 Heroes", value="2", description="Bring 2 heroes (up to 6 skills)"),
            discord.SelectOption(label="3 Heroes", value="3", description="Bring 3 heroes (up to 9 skills)")
        ]
        
        hero_count_select = ui.Select(
            placeholder="Choose number of heroes...",
            options=hero_count_options
        )
        hero_count_select.callback = self.hero_count_callback
        self.add_item(hero_count_select)
    
    async def hero_count_callback(self, interaction: Interaction):
        hero_count = int(interaction.data['values'][0])
        
        embed = discord.Embed(
            title="🐻 Rally Captain Hero Selection",
            description=f"**Captain:** {self.captain_name}\\n**Heroes to configure:** {hero_count}\\n\\nLet's set up your heroes...",
            color=0x0099ff
        )
        
        # Switch to captain multi-hero configuration
        captain_view = CaptainMultiHeroView(self.captain_name, hero_count)
        await interaction.response.edit_message(embed=embed, view=captain_view)

class CaptainMultiHeroView(ui.View):
    def __init__(self, captain, hero_count):
        super().__init__(timeout=300)
        self.captain = captain
        self.hero_count = hero_count
        self.current_hero = 0
        self.captain_heroes = []  # Will store: [{'hero': name, 'skill': name, 'effect': value}, ...]
        
        # Start with first hero selection
        self.show_hero_selection()
    
    def show_hero_selection(self):
        self.clear_items()
        
        # Add hero selection for current position
        hero_options = []
        for hero in HEROES:
            hero_options.append(discord.SelectOption(
                label=hero,
                value=hero,
                description=f"Select {hero} as captain hero #{self.current_hero + 1}"
            ))
        
        hero_select = ui.Select(
            placeholder=f"Choose captain hero #{self.current_hero + 1}...",
            options=hero_options
        )
        hero_select.callback = self.captain_hero_callback
        self.add_item(hero_select)
    
    async def captain_hero_callback(self, interaction: Interaction):
        selected_hero = interaction.data['values'][0]
        
        embed = discord.Embed(
            title="🐻 Rally Captain Hero Configuration",
            description=f"**Captain:** {self.captain}\\n**Current Hero:** {selected_hero}\\n\\nSelect expedition skill for {selected_hero}:",
            color=0x0099ff
        )
        
        self.clear_items()
        skill_options = []
        for skill_name in HERO_SKILLS[selected_hero].keys():
            skill_options.append(discord.SelectOption(
                label=skill_name,
                value=f"{selected_hero}|{skill_name}",
                description=f"{HERO_SKILLS[selected_hero][skill_name]['effect']}"
            ))
        
        skill_select = ui.Select(
            placeholder="Choose expedition skill...",
            options=skill_options
        )
        skill_select.callback = self.captain_skill_callback
        self.add_item(skill_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def captain_skill_callback(self, interaction: Interaction):
        selected = interaction.data['values'][0]
        hero_name, skill_name = selected.split('|')
        skill_effects = HERO_SKILLS[hero_name][skill_name]
        
        embed = discord.Embed(
            title="🐻 Rally Captain Hero Configuration",
            description=f"**Captain:** {self.captain}\\n**Current Hero:** {hero_name}\\n**Selected Skill:** {skill_name}\\n\\nNow select the effect level:",
            color=0x0099ff
        )
        
        # Add effect level selection
        self.clear_items()
        effect_options = []
        for i, value in enumerate(skill_effects['values']):
            effect_options.append(discord.SelectOption(
                label=f"Level {i+1}: +{value}%",
                value=f"{hero_name}|{skill_name}|{value}",
                description=f"{skill_effects['effect']} +{value}%"
            ))
        
        effect_select = ui.Select(
            placeholder="Choose effect level...",
            options=effect_options
        )
        effect_select.callback = self.captain_effect_callback
        self.add_item(effect_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def captain_effect_callback(self, interaction: Interaction):
        selected = interaction.data['values'][0]
        hero_name, skill_name, effect_value = selected.split('|')
        effect_value = int(effect_value)
        
        # Save this captain hero
        self.captain_heroes.append({
            'hero': hero_name,
            'skill': skill_name,
            'effect': effect_value
        })
        
        self.current_hero += 1
        
        # Check if we need more captain heroes
        if self.current_hero < self.hero_count:
            embed = discord.Embed(
                title="🐻 Rally Captain Hero Configuration",
                description=f"**Captain:** {self.captain}\\n**Heroes Configured:** {self.current_hero}/{self.hero_count}\\n\\n✅ Hero #{self.current_hero} configured! Setting up next hero...",
                color=0x0099ff
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Small delay then show next hero selection
            import asyncio
            await asyncio.sleep(1)
            
            embed = discord.Embed(
                title="🐻 Rally Captain Hero Configuration", 
                description=f"**Captain:** {self.captain}\\n**Heroes Configured:** {self.current_hero}/{self.hero_count}\\n\\n⚔️ Select captain hero #{self.current_hero + 1}:",
                color=0x0099ff
            )
            
            self.show_hero_selection()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            # All captain heroes configured, show summary and move to joiners
            await self.show_captain_summary(interaction)
    
    async def show_captain_summary(self, interaction: Interaction):
        # Calculate captain total (additive)
        captain_total = sum(hero['effect'] for hero in self.captain_heroes)
        
        summary_lines = [f"**Rally Captain:** {self.captain}"]
        for i, hero in enumerate(self.captain_heroes):
            summary_lines.append(f"**Hero {i+1}:** {hero['hero']} - {hero['skill']} (+{hero['effect']}%)")
        
        summary_lines.append(f"\\n🎯 **Captain Total Bonus:** +{captain_total}% (additive)")
        
        embed = discord.Embed(
            title="🐻 Rally Captain Setup Complete!",
            description="\\n".join(summary_lines) + "\\n\\n✅ Captain ready! Now configure rally joiners:",
            color=0x00ff00
        )
        
        # Add joiner count selection
        self.clear_items()
        joiner_options = []
        for i in range(1, 5):
            joiner_options.append(discord.SelectOption(
                label=f"{i} Rally Member{'s' if i > 1 else ''}",
                value=str(i),
                description=f"Add {i} rally member{'s' if i > 1 else ''} (contributes to 4 skill pool)"
            ))
        
        joiner_select = ui.Select(
            placeholder="How many rally members? (1-4 recommended)",
            options=joiner_options
        )
        joiner_select.callback = lambda inter: self.joiner_count_callback(inter, captain_total)
        self.add_item(joiner_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def joiner_count_callback(self, interaction: Interaction, captain_total):
        joiner_count = int(interaction.data['values'][0])
        
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Configuration",
            description=f"**Rally Captain:** {self.captain} ✅\\n**Rally Members to configure:** {joiner_count}\\n\\nLet's configure rally members...",
            color=0x0099ff
        )
        
        # Switch to joiner configuration (now they contribute to a pool of 4 skills)
        joiner_view = JoinerPoolConfigView(self.captain, captain_total, joiner_count)
        await interaction.response.edit_message(embed=embed, view=joiner_view)

# Joiner Pool Configuration Class (implements 4 highest-level first skills rule)
class JoinerPoolConfigView(ui.View):
    def __init__(self, captain, captain_total, joiner_count):
        super().__init__(timeout=300)
        self.captain = captain
        self.captain_total = captain_total
        self.joiner_count = joiner_count
        self.joiners = []  # Will store all joiner submissions
        self.current_joiner = 0
        
        # Start with first joiner selection
        self.show_joiner_selection()
    
    def show_joiner_selection(self):
        self.clear_items()
        
        # Add hero selection for current joiner
        hero_options = []
        for hero in HEROES:
            # Get first skill for preview
            first_skill = list(HERO_SKILLS[hero].keys())[0]
            hero_options.append(discord.SelectOption(
                label=hero,
                value=hero,
                description=f"First skill: {first_skill} ({HERO_SKILLS[hero][first_skill]['effect']})"
            ))
        
        hero_select = ui.Select(
            placeholder=f"Choose rally member #{self.current_joiner + 1} hero...",
            options=hero_options
        )
        hero_select.callback = self.joiner_hero_callback
        self.add_item(hero_select)
    
    async def joiner_hero_callback(self, interaction: Interaction):
        selected_hero = interaction.data['values'][0]
        
        # Get the first expedition skill for this hero (PDF rule)
        skill_name = list(HERO_SKILLS[selected_hero].keys())[0]
        skill_data = HERO_SKILLS[selected_hero][skill_name]
        
        embed = discord.Embed(
            title="🐻 Rally Member Configuration",
            description=f"**Rally Captain:** {self.captain} ✅\\n**Rally Member #{self.current_joiner + 1}:** {selected_hero}\\n**Auto-Selected Skill:** {skill_name}\\n**Effect:** {skill_data['effect']}\\n\\nSelect skill level:",
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
                title="🐻 Rally Member Configuration",
                description=f"**Rally Captain:** {self.captain} ✅\\n**Rally Members Configured:** {self.current_joiner}/{self.joiner_count}\\n\\n✅ Member #{self.current_joiner} configured! Setting up next member...",
                color=0x0099ff
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
            # Small delay then show next joiner selection
            import asyncio
            await asyncio.sleep(1)
            
            embed = discord.Embed(
                title="🐻 Rally Member Configuration", 
                description=f"**Rally Captain:** {self.captain} ✅\\n**Rally Members Configured:** {self.current_joiner}/{self.joiner_count}\\n\\n⚔️ Select rally member #{self.current_joiner + 1} hero:",
                color=0x0099ff
            )
            
            self.show_joiner_selection()
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            # All joiners configured, calculate final rally
            await self.show_final_rally_calculation(interaction)
    
    async def show_final_rally_calculation(self, interaction: Interaction):
        # Implement 4 highest-level first skills rule from PDF
        
        # Sort joiners by effect value (highest first) and take top 4
        sorted_joiners = sorted(self.joiners, key=lambda x: x['effect'], reverse=True)
        top_4_joiners = sorted_joiners[:4]  # Only top 4 highest-level skills count
        
        # Calculate final rally bonus
        # Captain total is additive (already calculated)
        # Top 4 joiner skills are added to create the rally total
        
        summary_lines = [f"**Rally Captain:** {self.captain} (+{self.captain_total}%)"]
        
        joiner_total = 0
        for i, joiner in enumerate(top_4_joiners):
            summary_lines.append(f"**Top Member {i+1}:** {joiner['hero']} (+{joiner['effect']}%)")
            joiner_total += joiner['effect']
        
        # Show excluded joiners if any
        if len(self.joiners) > 4:
            excluded = self.joiners[4:]
            summary_lines.append(f"\\n⚠️ **Excluded Members:** {len(excluded)} (only top 4 skills count)")
            for joiner in excluded:
                summary_lines.append(f"  - {joiner['hero']} (+{joiner['effect']}%) - Not counted")
        
        total_rally_bonus = self.captain_total + joiner_total
        
        if total_rally_bonus < 50:
            color = 0xff0000
            status = "Below Optimal"
        elif total_rally_bonus <= 100:
            color = 0xffa500  
            status = "Good Setup"
        else:
            color = 0x00ff00
            status = "Excellent!"
        
        summary_lines.append(f"\n🎯 **Total Rally Size:** {len(self.joiners) + 1} members")
        summary_lines.append(f"⚔️ **Active Skills:** Captain ({self.captain_total}%) + Top 4 Members ({joiner_total}%)")
        summary_lines.append(f"\n📊 **Total Rally Bonus:** {total_rally_bonus}% ({status})")
        summary_lines.append(f"📈 **Calculation Method:** Captain (additive) + Top 4 Member Skills (per PDF)")
        
        embed = discord.Embed(
            title="🧮 Bear Hunt Rally Calculation (PDF Rules)",
            description="\n".join(summary_lines),
            color=color
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

if __name__ == "__main__":
    print("🚀 Starting Bear Hunt Rally Calculator for deployment...")
    bot.run(BOT_TOKEN)