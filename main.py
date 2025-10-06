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
        "Beast's Vigor": {"effect": "Health Up", "values": [5, 10, 15, 20, 25]},
        "Pierce": {"effect": "Enemy Troop Defense Down", "values": [4, 8, 12, 16, 20]}
    },
    "Gordon": {
        "Mend": {"effect": "Healing Speed Up", "values": [10, 20, 30, 40, 50]},
        "Intimidation": {"effect": "Enemy Troop Attack Down", "values": [4, 8, 12, 16, 20]}
    },
    "Fahd": {
        "Resourceful": {"effect": "Construction Speed + Cost Down", "values": [3, 6, 9, 12, 15]},
        "Positional Batter": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]}
    },
    "Saul": {
        "Resourceful": {"effect": "Construction Speed + Cost Down", "values": [3, 6, 9, 12, 15]},
        "Positional Batter": {"effect": "Lethality Up", "values": [5, 10, 15, 20, 25]}
    },
    "Hilde": {
        "Noble Path (Attack Up)": {"effect": "Attack Up", "values": [3, 6, 9, 12, 15]},
        "Noble Path (Defense Up)": {"effect": "Defense Up", "values": [2, 4, 6, 8, 10]},
        "Elixir of Strength": {"effect": "Damage Up", "values": [120, 140, 160, 180, 200]},
        "Trial by Fire": {"effect": "Damage Taken Chance Down", "values": [8, 16, 24, 32, 40]}
    },
    "Eric": {
        "Holy Warrior": {"effect": "Enemy Troop Attack Down", "values": [4, 8, 12, 16, 20]},
        "Conviction": {"effect": "Damage Taken Down", "values": [4, 8, 12, 16, 20]},
        "Exhortation": {"effect": "Health Up", "values": [5, 10, 15, 20, 25]}
    }
}

class JoinerConfigView(ui.View):
    def __init__(self, captain, captain_skill, captain_effect, joiner_count):
        super().__init__(timeout=300)
        self.captain = captain
        self.captain_skill = captain_skill
        self.captain_effect = captain_effect
        self.joiner_count = joiner_count
        self.joiners = []  # List to store joiner configurations
        self.current_joiner = 0  # Which joiner we're currently configuring
        
        # Start configuring the first joiner
        self.setup_joiner_selection()
    
    def setup_joiner_selection(self):
        self.clear_items()
        
        # Joiner hero dropdown - all heroes available (duplicates allowed)
        joiner_select = ui.Select(
            placeholder=f"Select Joiner #{self.current_joiner + 1} Hero (duplicates allowed)",
            options=[
                discord.SelectOption(
                    label=hero, 
                    value=hero, 
                    emoji="⚔️",
                    description=f"Any hero can be selected multiple times"
                )
                for hero in HERO_SKILLS.keys()
            ]
        )
        joiner_select.callback = self.joiner_hero_callback
        self.add_item(joiner_select)
        
        # Add back button if not on first joiner
        if self.current_joiner > 0:
            back_btn = ui.Button(
                label="← Back to Previous Joiner", 
                style=discord.ButtonStyle.secondary, 
                emoji="↩️"
            )
            back_btn.callback = self.back_callback
            self.add_item(back_btn)
    
    async def joiner_hero_callback(self, interaction: Interaction):
        selected_joiner = interaction.data['values'][0]
        print(f"🎯 Selected joiner #{self.current_joiner + 1}: {selected_joiner}")
        
        # Show skill selection for this joiner
        remaining_joiners = self.joiner_count - self.current_joiner - 1
        progress_text = f"**Progress:** Configuring joiner {self.current_joiner + 1} of {self.joiner_count}"
        if remaining_joiners > 0:
            progress_text += f" ({remaining_joiners} more to go)"
        
        # Show current rally composition
        current_heroes = [self.captain] + [j['hero'] for j in self.joiners]
        if len(current_heroes) > 1:
            heroes_text = f"**Current Heroes:** {', '.join(current_heroes)}, {selected_joiner}"
        else:
            heroes_text = f"**Current Heroes:** {self.captain}, {selected_joiner}"
        
        embed = discord.Embed(
            title=f"🐻 Configure Joiner #{self.current_joiner + 1}: {selected_joiner}",
            description=f"**Rally Captain:** {self.captain} ✅\n{progress_text}\n{heroes_text}\n\n🎯 Select expedition skill for {selected_joiner}:",
            color=0x0099ff
        )
        
        self.clear_items()
        
        # Add skill dropdown for the selected joiner
        skills = HERO_SKILLS[selected_joiner]
        skill_select = ui.Select(
            placeholder=f"Select {selected_joiner}'s expedition skill",
            options=[
                discord.SelectOption(
                    label=skill,
                    value=skill,
                    description=f"Effect: {effects['effect']}",
                    emoji="🎯"
                )
                for skill, effects in skills.items()
            ]
        )
        skill_select.callback = lambda i: self.joiner_skill_callback(i, selected_joiner)
        self.add_item(skill_select)
        
        # Add back button to change hero selection
        back_btn = ui.Button(
            label="← Change Hero Selection", 
            style=discord.ButtonStyle.secondary, 
            emoji="🔄"
        )
        back_btn.callback = self.back_to_hero_selection
        self.add_item(back_btn)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def joiner_skill_callback(self, interaction: Interaction, joiner_hero):
        selected_skill = interaction.data['values'][0]
        skill_effects = HERO_SKILLS[joiner_hero][selected_skill]
        
        print(f"🎯 Joiner #{self.current_joiner + 1} skill: {selected_skill}")
        
        # Show effect level selection
        embed = discord.Embed(
            title=f"🐻 Configure Joiner #{self.current_joiner + 1}: {joiner_hero}",
            description=f"**Skill:** {selected_skill}\n**Effect:** {skill_effects['effect']}\n\nSelect effect level:",
            color=0x0099ff
        )
        
        self.clear_items()
        
        # Add effect level dropdown
        effect_select = ui.Select(
            placeholder="Select effect level (1-5)",
            options=[
                discord.SelectOption(
                    label=f"Level {level}",
                    value=str(level),
                    description=f"Effect: +{skill_effects['values'][level-1]}%",
                    emoji="⭐"
                )
                for level in range(1, 6)
            ]
        )
        effect_select.callback = lambda i: self.joiner_effect_callback(i, joiner_hero, selected_skill)
        self.add_item(effect_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def joiner_effect_callback(self, interaction: Interaction, joiner_hero, joiner_skill):
        effect_level = int(interaction.data['values'][0])
        skill_effects = HERO_SKILLS[joiner_hero][joiner_skill]
        effect_value = skill_effects['values'][effect_level-1]
        
        print(f"🎯 Joiner #{self.current_joiner + 1} effect level: {effect_level} (+{effect_value}%)")
        
        # Store this joiner's configuration
        joiner_config = {
            'hero': joiner_hero,
            'skill': joiner_skill,
            'effect_level': effect_level,
            'effect_value': effect_value
        }
        self.joiners.append(joiner_config)
        self.current_joiner += 1
        
        # Check if we need to configure more joiners
        if self.current_joiner < self.joiner_count:
            # Show progress and configure next joiner
            embed = discord.Embed(
                title="🐻 Bear Hunt Rally Configuration",
                description=f"**Rally Captain:** {self.captain} ✅\n**Joiners Configured:** {self.current_joiner}/{self.joiner_count}\n**Current Rally:** {', '.join([self.captain] + [j['hero'] for j in self.joiners])}\n\n✅ Joiner #{self.current_joiner} configured! Setting up next joiner...",
                color=0x0099ff
            )
            await interaction.response.edit_message(embed=embed, view=self)
            
            # Small delay for better UX, then setup next joiner
            import asyncio
            await asyncio.sleep(1)
            self.setup_joiner_selection()
            
            # Update the message with the new joiner selection
            embed = discord.Embed(
                title="🐻 Bear Hunt Rally Configuration",
                description=f"**Rally Captain:** {self.captain} ✅\n**Joiners Configured:** {self.current_joiner}/{self.joiner_count}\n**Current Rally:** {', '.join([self.captain] + [j['hero'] for j in self.joiners])}\n\n⚔️ Select joiner #{self.current_joiner + 1} hero:",
                color=0x0099ff
            )
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            # All joiners configured, show final summary
            await self.show_final_summary(interaction)
    
    async def back_to_hero_selection(self, interaction: Interaction):
        """Go back to hero selection for current joiner"""
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Configuration",
            description=f"**Rally Captain:** {self.captain} ✅\n**Joiners Configured:** {self.current_joiner}/{self.joiner_count}\n**Current Rally:** {', '.join([self.captain] + [j['hero'] for j in self.joiners])}\n\n⚔️ Select joiner #{self.current_joiner + 1} hero:",
            color=0x0099ff
        )
        
        self.setup_joiner_selection()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def back_callback(self, interaction: Interaction):
        """Go back to previous joiner configuration"""
        if self.current_joiner > 0:
            # Remove the last configured joiner
            if self.joiners:
                last_joiner = self.joiners.pop()
            
            self.current_joiner -= 1
            
            embed = discord.Embed(
                title="🐻 Bear Hunt Rally Configuration",
                description=f"**Rally Captain:** {self.captain} ✅\n**Joiners Configured:** {self.current_joiner}/{self.joiner_count}\n**Current Rally:** {', '.join([self.captain] + [j['hero'] for j in self.joiners])}\n\n⚔️ Reconfigure joiner #{self.current_joiner + 1}:",
                color=0x0099ff
            )
            
            self.setup_joiner_selection()
            await interaction.response.edit_message(embed=embed, view=self)

    async def show_final_summary(self, interaction: Interaction):
        # Build summary description allowing duplicate heroes
        summary_lines = [f"**Rally Captain:** {self.captain}"]
        summary_lines.append(f"├─ **Skill:** {self.captain_skill}")
        summary_lines.append(f"└─ **Effect:** +{self.captain_effect}%\n")
        
        summary_lines.append(f"**Joiner Heroes ({len(self.joiners)}):**")
        for i, joiner in enumerate(self.joiners, 1):
            summary_lines.append(f"{i}. **{joiner['hero']}** ⚔️")
            summary_lines.append(f"   ├─ **Skill:** {joiner['skill']}")
            summary_lines.append(f"   └─ **Effect:** +{joiner['effect_value']}%")
        
        # Show all heroes used (duplicates allowed)
        all_heroes = [self.captain] + [j['hero'] for j in self.joiners]
        summary_lines.append(f"\n🎯 **Total Rally Size:** {len(all_heroes)} heroes")
        summary_lines.append(f"📋 **Rally Composition:** {', '.join(all_heroes)}")
        
        # Count hero frequencies
        from collections import Counter
        hero_counts = Counter(all_heroes)
        if any(count > 1 for count in hero_counts.values()):
            duplicate_info = []
            for hero, count in hero_counts.items():
                if count > 1:
                    duplicate_info.append(f"{hero} x{count}")
            if duplicate_info:
                summary_lines.append(f"🔄 **Duplicates:** {', '.join(duplicate_info)}")
        
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Setup Complete!",
            description="\n".join(summary_lines) + "\n\n✅ Ready to calculate rally bonus!",
            color=0x00ff00
        )
        
        self.clear_items()
        
        # Add calculate button
        calc_btn = ui.Button(
            label="Calculate Rally Bonus", 
            style=discord.ButtonStyle.primary, 
            emoji="🧮"
        )
        calc_btn.callback = self.calculate_callback
        self.add_item(calc_btn)
        
        # Add reset button
        reset_btn = ui.Button(
            label="Start Over", 
            style=discord.ButtonStyle.secondary, 
            emoji="🔄"
        )
        reset_btn.callback = self.reset_callback
        self.add_item(reset_btn)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def calculate_callback(self, interaction: Interaction):
        # Calculate rally bonus with multiplicative stacking for different heroes
        
        # Group bonuses by effect operation (hero type)
        bonus_effects = {}
        all_heroes = [(self.captain, self.captain_effect)]
        for joiner in self.joiners:
            all_heroes.append((joiner['hero'], joiner['effect_value']))
        
        # Group bonuses by hero effect operation
        for hero, effect_value in all_heroes:
            effect_op = HERO_EFFECT_OPS.get(hero, 999)  # Default op if not found
            if effect_op not in bonus_effects:
                bonus_effects[effect_op] = 0
            bonus_effects[effect_op] += effect_value
        
        # Calculate multiplicative damage bonus
        damage_multiplier = 1.0
        for effect_op, total_bonus in bonus_effects.items():
            damage_multiplier *= (1 + total_bonus / 100)
        
        # Convert back to percentage for display
        total_percentage = (damage_multiplier - 1) * 100
        
        # Determine color based on bonus percentage
        if total_percentage < 100:
            color = 0xff0000  # Red
            status = "Below Optimal"
        elif total_percentage <= 110:
            color = 0xff8c00  # Orange
            status = "Good"
        else:
            color = 0x00ff00  # Green
            status = "Excellent"
        
        # Build detailed result
        result_lines = [f"**Rally Captain:** {self.captain} (+{self.captain_effect}%)"]
        for i, joiner in enumerate(self.joiners, 1):
            result_lines.append(f"**Joiner {i}:** {joiner['hero']} (+{joiner['effect_value']}%)")
        
        # Add multiplicative calculation details
        if len(bonus_effects) > 1:
            calc_details = []
            for effect_op, bonus in bonus_effects.items():
                # Find hero name for this effect op
                hero_name = next((hero for hero, op in HERO_EFFECT_OPS.items() if op == effect_op), f"Effect{effect_op}")
                calc_details.append(f"{hero_name} group: +{bonus}% → ×{1 + bonus/100:.2f}")
            
            result_lines.append(f"\n**🔄 Multiplicative Stacking:**")
            result_lines.extend(calc_details)
            result_lines.append(f"**Final multiplier:** {damage_multiplier:.3f}")
        
        embed = discord.Embed(
            title="🧮 Bear Hunt Rally Calculation",
            description="\n".join(result_lines),
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


class SkillConfigView(ui.View):
    def __init__(self, captain):
        super().__init__(timeout=300)
        self.captain = captain
        self.selected_skill = None
        self.selected_effect = None
        self.joiner_count = 0  # Track how many joiners user wants
        
        # Start with skill selection
        self.setup_skill_selection()
    
    def setup_skill_selection(self):
        self.clear_items()
        
        # Get skills for the selected captain
        captain_skills = HERO_SKILLS[self.captain]
        
        # Create skill dropdown
        skill_select = ui.Select(
            placeholder="Select captain's expedition skill",
            options=[
                discord.SelectOption(
                    label=skill,
                    value=skill,
                    description=f"Effect: {effects['effect']}",
                    emoji="🎯"
                )
                for skill, effects in captain_skills.items()
            ]
        )
        skill_select.callback = self.skill_callback
        self.add_item(skill_select)
    
    async def skill_callback(self, interaction: Interaction):
        selected_skill = interaction.data['values'][0]
        self.selected_skill = selected_skill
        
        skill_effects = HERO_SKILLS[self.captain][selected_skill]
        
        print(f"🎯 Skill 1 selected: {selected_skill}")
        
        embed = discord.Embed(
            title=f"🐻 Captain: {self.captain}",
            description=f"**Rally Captain:** {self.captain}\n**Selected Skill:** {selected_skill}\n**Effect:** {skill_effects['effect']}\n\nNow select the effect level:",
            color=0x0099ff
        )
        
        self.clear_items()
        
        # Add effect level selection
        effect_select = ui.Select(
            placeholder="Select effect level (1-5)",
            options=[
                discord.SelectOption(
                    label=f"Level {level}",
                    value=str(level),
                    description=f"Effect: +{skill_effects['values'][level-1]}%",
                    emoji="⭐"
                )
                for level in range(1, 6)
            ]
        )
        effect_select.callback = self.effect_callback
        self.add_item(effect_select)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def effect_callback(self, interaction: Interaction):
        effect_level = int(interaction.data['values'][0])
        skill_effects = HERO_SKILLS[self.captain][self.selected_skill]
        effect_value = skill_effects['values'][effect_level-1]
        
        self.selected_effect = effect_value
        
        print(f"🎯 Effect selected: {self.selected_skill} - {effect_value}%")
        
        # Show completed captain setup and joiner selection
        skill_name = self.selected_skill
        effect_name = f"Level {effect_level}"
        
        embed = discord.Embed(
            title="🐻 Bear Hunt Rally Setup Complete!",
            description=f"**Rally Captain:** {self.captain}\n**Skill:** {skill_name}\n**Effect:** {effect_name} (+{effect_value}%)\n\n✅ Captain ready! Now choose joiner heroes:",
            color=0x00ff00  # Green to indicate ready
        )
        
        # NOW add the joiner count selection and calculate button
        self.clear_items()
        
        # Add joiner count selection dropdown (minimum 1 joiner required)
        joiner_options = []
        for i in range(1, 5):  # 1 to 4 joiners (minimum 1 required)
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
        self.joiner_count = joiner_count  # Store the joiner count
        print(f"🎯 User wants {joiner_count} joiner heroes")
        
        # Start joiner configuration with the new system
        embed = discord.Embed(
            title="🐻 Configure Joiner Heroes",
            description=f"**Rally Captain:** {self.captain} ✅\n**Joiners to configure:** {joiner_count}\n\nLet's configure each joiner hero...",
            color=0x0099ff
        )
        
        # Switch to the joiner configuration view
        joiner_view = JoinerConfigView(self.captain, self.selected_skill, self.selected_effect, joiner_count)
        await interaction.response.edit_message(embed=embed, view=joiner_view)

    async def calculate_callback(self, interaction: Interaction):
        # Simple calculation for captain-only rally (if no joiners selected)
        captain_bonus = self.selected_effect
        diversity_bonus = 0  # Additional bonus for hero diversity (would be calculated with joiners)
        total_bonus = captain_bonus + diversity_bonus
        
        # Determine color based on bonus percentage
        if total_bonus < 100:
            color = 0xff0000  # Red
            status = "Below Optimal"
        elif total_bonus <= 110:
            color = 0xff8c00  # Orange
            status = "Good"
        else:
            color = 0x00ff00  # Green
            status = "Excellent"
        
        embed = discord.Embed(
            title="🧮 Bear Hunt Rally Calculation",
            description=f"**Rally Captain:** {self.captain} (+{captain_bonus}%)",
            color=color
        )
        embed.add_field(name="📊 Total Rally Bonus", value=f"**{total_bonus}%** ({status})", inline=False)
        embed.add_field(name="📈 Note", value="Add joiner heroes for higher bonuses!", inline=False)
        
        self.clear_items()
        
        # Add new rally button
        new_rally_btn = ui.Button(label="Calculate New Rally", style=discord.ButtonStyle.primary, emoji="🆕")
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
        print(f"🎯 Captain selected: {self.captain}")
        
        embed = discord.Embed(
            title=f"🐻 Rally Captain: {self.captain}",
            description=f"**Rally Captain:** {self.captain}\n\nNow use the buttons below to configure skills and joiners.",
            color=0x0099ff
        )
        
        # Switch to skill configuration
        skill_view = SkillConfigView(self.captain)
        await interaction.response.edit_message(embed=embed, view=skill_view)

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} has logged in!')
    print('🐻 Bear Hunt Rally Calculator ready for deployment!')

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully"""
    if isinstance(error, commands.CommandNotFound):
        # Ignore command not found errors (don't crash the bot)
        print(f"⚠️ Unknown command attempted: {ctx.message.content}")
        return
    else:
        # Log other errors but don't crash
        print(f"❌ Error in command {ctx.command}: {error}")

@bot.command(name='hello')
async def hello(ctx):
    """Simple hello command for testing"""
    await ctx.send("🐻 Hello! Use `!rally` to start the Bear Hunt Rally Calculator!")

@bot.command(name='rally')
async def rally_calculator(ctx):
    """Start the Bear Hunt Rally Calculator"""
    print(f'🐻 Rally calculator started by {ctx.author}')
    
    embed = discord.Embed(
        title="🐻 Bear Hunt Rally Calculator",
        description="Configure your Bear Hunt rally team for maximum effectiveness!\n\n**Features:**\n⚔️ 11 unique heroes with expedition skills\n🔄 Multiplicative bonuses for hero diversity\n📊 Color-coded optimization results\n🎯 Support for duplicate heroes",
        color=0x0099ff
    )
    
    view = RallyCalculatorView()
    await ctx.send(embed=embed, view=view)

@bot.slash_command(description="Check bot and services status")
async def status(ctx):
    """Check the status of all bot services and infrastructure"""
    try:
        import urllib.request
        import urllib.error
        from datetime import datetime
        import time
        
        # Start timing
        start_time = time.time()
        
        embed = discord.Embed(
            title="🔍 System Status Check",
            color=0x00ff00
        )
        
        # Bot Status
        embed.add_field(
            name="🤖 Discord Bot",
            value=f"✅ Online\n🕐 Latency: {round(bot.latency * 1000)}ms",
            inline=True
        )
        
        # Keep-alive Web Server Status
        web_status = "❌ Offline"
        web_response_time = "N/A"
        try:
            web_start = time.time()
            with urllib.request.urlopen('http://localhost:8080/ping', timeout=5) as response:
                web_response_time = f"{round((time.time() - web_start) * 1000)}ms"
                web_status = "✅ Online"
        except Exception as e:
            web_status = f"❌ Error: {str(e)[:30]}..."
        
        embed.add_field(
            name="🌐 Keep-Alive Server",
            value=f"{web_status}\n🕐 Response: {web_response_time}",
            inline=True
        )
        
        # External Monitoring Status
        koyeb_status = "❌ Offline"
        koyeb_response_time = "N/A"
        try:
            koyeb_start = time.time()
            koyeb_url = "https://collective-wildebeest-discordpxt272-f4306de1.koyeb.app/health"
            with urllib.request.urlopen(koyeb_url, timeout=10) as response:
                koyeb_response_time = f"{round((time.time() - koyeb_start) * 1000)}ms"
                if response.read().decode() == "OK":
                    koyeb_status = "✅ Online"
                else:
                    koyeb_status = "⚠️ Responding but not OK"
        except Exception as e:
            koyeb_status = f"❌ Error: {str(e)[:30]}..."
        
        embed.add_field(
            name="☁️ Koyeb Public Endpoint",
            value=f"{koyeb_status}\n🕐 Response: {koyeb_response_time}",
            inline=True
        )
        
        # Rally Calculator Test
        calculator_status = "✅ Ready"
        hero_count = len(HEROES)
        
        embed.add_field(
            name="🧮 Rally Calculator",
            value=f"{calculator_status}\n👥 Heroes: {hero_count}/11",
            inline=True
        )
        
        # Monitoring Services
        embed.add_field(
            name="📊 External Monitoring",
            value="🔗 [UptimeRobot](https://stats.uptimerobot.com/zxDtL1vced)\n🔗 [Cron-job.org](https://console.cron-job.org/)",
            inline=True
        )
        
        # System Info
        embed.add_field(
            name="⚙️ System Info",
            value=f"🐍 Python Runtime\n🌐 Flask Keep-Alive\n🔄 Self-Ping Active",
            inline=True
        )
        
        # Overall status
        total_time = round((time.time() - start_time) * 1000)
        
        if "✅" in web_status and "✅" in koyeb_status:
            overall_status = "🟢 All Systems Operational"
            embed.color = 0x00ff00
        elif "✅" in web_status or "✅" in koyeb_status:
            overall_status = "🟡 Partial Service Available"
            embed.color = 0xffff00
        else:
            overall_status = "🔴 Service Issues Detected"
            embed.color = 0xff0000
        
        embed.add_field(
            name="📈 Overall Status",
            value=f"{overall_status}\n⏱️ Check completed in {total_time}ms",
            inline=False
        )
        
        embed.set_footer(
            text=f"Status checked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} • Use /rally_calculator to start"
        )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        # Fallback simple status
        await ctx.send(f"🔍 **Quick Status Check**\n✅ Bot Online\n🕐 Latency: {round(bot.latency * 1000)}ms\n❌ Error in detailed check: {str(e)}")

# Also add a simple ping command that works immediately
@bot.slash_command(description="Simple ping test")
async def ping(ctx):
    """Simple ping command to test bot responsiveness"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency}ms")

if __name__ == "__main__":
    print("🚀 Starting Bear Hunt Rally Calculator for deployment...")
    bot.run(BOT_TOKEN)