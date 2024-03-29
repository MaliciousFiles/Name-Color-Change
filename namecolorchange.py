from discord.ext import commands
import discord
import random
from dotenv import get_key
from appdirs import user_data_dir
import os

roaming_dir = user_data_dir("Name Color Change", "MaliciousFiles", roaming=True)
if not os.path.exists(roaming_dir):
    os.makedirs(roaming_dir)

env_file = os.path.join(roaming_dir, ".env")
if not os.path.exists(env_file):
    with open(env_file, "x"):
        pass

bot = commands.Bot(command_prefix=">", case_insensitive=True, intents=discord.Intents(message_content=True))
bot.remove_command("help")

COLORS = ["default", "red", "dark_red", "orange", "dark_orange", "gold", "dark_gold", "green", "dark_green", "teal", "dark_teal", "blue", "dark_blue", "blurple", "magenta", "dark_magenta", "purple", "dark_purple", "greyple", "lighter_gray", "light_gray", "darkple", "gray", "dark_gray", "darker_gray", "dark_theme", "random", "expanded_random"]

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=">help"))

def parse_color(color):
    rgb = None

    if color[0] == "#":
        color = color[1:]
        if len(color) != 6:
            return None

        try:
            rgb = tuple(int(color[i:i+2], 16) for i in range(0, 6, 2))
        except ValueError:
            return None
    elif color[:3] == "rgb":
        color = color[4:].replace(" ", "").replace(")", "")
        if len(color.split(",")) != 3:
            return None

        try:
            rgb = tuple(int(i) for i in color.split(","))
        except ValueError:
            return None
    else:
        color = color.replace(" ", "_")

        try:
            _locals = locals()
            exec(f"rgb = discord.Colour.{color}().to_rgb()", globals(), _locals)
            rgb = _locals["rgb"]
        except (AttributeError, SyntaxError):
            return None

    return rgb

async def send_fail_msg(ctx, msg):
    embed = discord.Embed(title="Failure", description=msg, colour=discord.Colour.dark_red())
    await ctx.send(embed=embed)

async def send_success_msg(ctx, msg, color):
    if color is None:
        embed = discord.Embed(title="Success", description=msg)
    else:
        embed = discord.Embed(title="Success", description=msg, colour=color)
    await ctx.send(embed=embed)

async def send_forbidden_msg(ctx, msg):
    await ctx.send(embed=discord.Embed(title="Missing Permissions",
        description="I don't have enough permissions to "+msg+"!", colour=discord.Colour.dark_red()))

async def set_namecolor(ctx, member, color):
    if member is None:
        member = ctx.author
        display_name = "N"
    elif member != ctx.author and not ctx.author.guild_permissions.manage_roles:
        await send_fail_msg(ctx, "You must have the Manage Roles permission to modify other members' roles!")
        return
    else:
        try:
            member = await ctx.guild.fetch_member(int(member))
        except ValueError:
            await ctx.send(embed=discord.Embed(title="Incorrect Input",
                description=f"**{member}** is not a number! To get a member's ID, set *User Settings>Advanced>Developer Mode* to true. Then right click the user and say *Copy ID*. Paste that here.", colour=discord.Colour.dark_red()))
            return
        display_name = member.name + "'s n"

    color = color.lower()
    if color == "help":
        await help(ctx)
        return

    role = discord.utils.get(ctx.guild.roles, name=member.name)

    try:
        color = COLORS[int(color)-1].replace("_", " ")
    except (ValueError, IndexError):
        pass

    display_color = ""

    if (color == "none"):
        try:
            await member.remove_roles(role)
        except discord.errors.Forbidden:
            await send_forbidden_msg(ctx, "remove "+role.mention+" from "+member.mention)
            return
        await send_success_msg(ctx, display_name+"ame color successfully removed!", None)
        return
    elif (color == "random"):
        color_choices = COLORS.copy()
        color_choices.remove("random").remove("expanded_random")
        color = random.choice(color_choices)
        display_color = "Random: "
    elif (color == "expanded random"):
        color = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
        display_color = "Expanded Random: "

    display_color += color.replace("_", " ").title().replace("Rgb", "rgb")

    parsed_color = parse_color(color)

    if parsed_color is None:
        await send_fail_msg(ctx, f"**{display_color}** is not a valid Hex Code, RGB tuple, or preset! Use `/namecolor help` or `>help` for help.")

        return

    disc_color = discord.Colour.from_rgb(parsed_color[0], parsed_color[1], parsed_color[2])

    if role is None:
        try:
            role = await ctx.guild.create_role(name=member.name, color=disc_color, mentionable=False)
        except discord.errors.Forbidden:
            await send_forbidden_msg(ctx, "create role '@"+member.name+"' for "+member.mention);
            return
        position=discord.utils.get(ctx.guild.roles, name=bot.user.name).position-1
        try:

            await role.edit(position=position)
        except discord.errors.Forbidden:
            await send_forbidden_msg(ctx, "move role "+role.mention+" to position"+position)
            return
    else:
        try:
            await role.edit(colour=disc_color)
        except discord.errors.Forbidden:
            await send_forbidden_msg(ctx, "change color of "+role.mention+" to "+disc_color)
            return

    if (not role in member.roles):
        try:
            await member.add_roles(role)
        except discord.errors.Forbidden:
            await send_forbidden_msg(ctx, "add role "+role.mention+" to "+member.mention)
            return

    await send_success_msg(ctx, display_name+f"ame color successfully changed to **{display_color}**!", disc_color)

@bot.command(name="namecolor")
async def namecolor_bot(ctx, color, member=None):
    await set_namecolor(ctx, member, color)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="NameColor Help", description="""
    ***Commands*** | Prefix is `>`
    **namecolor <color>**: *Sets your name color to **<color>**, which can be a Hex [#ffffff], RGB [rgb(255, 255, 255)], or a Preset [white]. `None` to clear.*
    **help**: *Shows this help page.*
    ------------------------------------------------------------
    ***Presets***
    >>> 1. Default
    2. Red
    3. Dark Red
    4. Orange
    5. Dark Orange
    6. Gold
    7. Dark Gold
    8. Green
    9. Dark Green
    10. Teal
    11. Dark Teal
    12. Blue
    13. Dark Blue
    14. Blurple
    15. Magenta
    16. Dark Magenta
    17. Purple
    18. Dark Purple
    19. Greyple
    20. Lighter Gray / Grey
    21. Light Gray / Grey
    22. Gray / Grey
    23. Dark Gray / Grey
    24. Darker Gray / Grey
    25. Dark Theme
    26. Random
    27. Expanded Random
    """, colour=discord.Colour.green())
    await ctx.send(embed=embed)

bot.run(get_key(env_file, "token"))