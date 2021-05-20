import discord, asyncio

svr = "purple"

REACTION_LOCK = asyncio.Lock()
ROLE_MESSAGE_ID = -1
ROLE_CHANNEL_ID = -1
EMOJI_ROLE_DICT = {
    "🔵": "blue",
    "🟤": "brown",
    "🟢": "green",
    "🟠": "orange",
    "🔴": "red",
    "⚪": "white",
    "🟡": "yellow",
}

ROLE_COLOURS = {
    "blue": 0x3884ff,
    "brown": 0xa0522d,
    "green": 0x34c431,
    "orange": 0xe08b2f,
    "red": 0xe32727,
    "white": 0xffffff,
    "yellow": 0xffc21c,
}

def main():
    TOKEN = open('token.txt', 'r').read().strip()
    intents = discord.Intents.default()
    intents.members = True 

    client = discord.Client(intents=intents)


    @client.event
    async def on_ready():
        global ROLE_MESSAGE_ID
        global ROLE_CHANNEL_ID
        global svr
        for g in client.guilds:
            if svr in g.name.lower():
                for tc in g.text_channels:
                    if tc.name == "roles":
                        ROLE_CHANNEL_ID = tc.id
                        async for message in tc.history(limit=10):
                            if message.author == client.user and message.embeds and "role" in message.embeds[0].title.lower():
                                ROLE_MESSAGE_ID = message.id
                        await setup_reaction_message(tc)
                        break
                await create_colour_roles(g)


        
        print("Bot Ready")
        print(ROLE_MESSAGE_ID)
    
    @client.event
    async def on_raw_reaction_add(payload):
        if payload.message_id == ROLE_MESSAGE_ID:
            user = payload.member
            user_id = payload.user_id
            if user != client.user:
                emoji = str(payload.emoji)
                if emoji in EMOJI_ROLE_DICT:
                    async with REACTION_LOCK:
                        for e in EMOJI_ROLE_DICT:
                            e_role = discord.utils.get(user.guild.roles, name=EMOJI_ROLE_DICT[e])
                            up_user = discord.utils.get(user.guild.members, id=user_id)
                            if e != emoji and e_role in up_user.roles:
                                c = user.guild.get_channel(ROLE_CHANNEL_ID)
                                await (await c.fetch_message(payload.message_id)).remove_reaction(e, user)
                                await user.remove_roles(discord.utils.get(user.guild.roles, name=EMOJI_ROLE_DICT[e]))
                            else:
                                if e == emoji:
                                    await user.add_roles(discord.utils.get(user.guild.roles, name=EMOJI_ROLE_DICT[emoji]))

    @client.event
    async def on_raw_reaction_remove(payload):
        if payload.message_id == ROLE_MESSAGE_ID:
            guild = client.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
            if user != client.user:
                emoji = str(payload.emoji)
                if emoji in EMOJI_ROLE_DICT:
                    await user.remove_roles(discord.utils.get(guild.roles, name=EMOJI_ROLE_DICT[emoji]))


    @client.event
    async def on_guild_join(guild):
        await create_colour_roles(guild)
        for tc in guild.text_channels:
            if tc.name == "roles":
                await setup_reaction_message(tc)
                break
        
    
    # Only here for testing and fixing stuff
    @client.event
    async def on_message(message):
        if message.author.guild_permissions.administrator or message.author.id == 204695987825016832:
            if message.content == "setup_reaction_message":
                await setup_reaction_message(message.channel)
                await message.delete()
            elif message.content == "update_roles":
                print("updating roles")
                await create_colour_roles(message.guild)

    client.run(TOKEN)

async def setup_reaction_message(tc):
    global ROLE_MESSAGE_ID
    # Build message
    reaction_message = discord.Embed(title="Roles", description=f"React to the following to get the relevant role\n", color=0x000000)
    if ROLE_MESSAGE_ID != -1:
        m = await tc.fetch_message(ROLE_MESSAGE_ID)
        await m.edit(embed=reaction_message)
    else:
        m = await tc.send(embed=reaction_message)
        ROLE_MESSAGE_ID = m.id
    for i in EMOJI_ROLE_DICT:
        await m.add_reaction(i)
    

async def create_colour_roles(guild):
    pos = len(await guild.fetch_roles()) - 3
    for role in ROLE_COLOURS:
        sr = discord.utils.get(guild.roles, name=role)
        if sr:
            await sr.edit(colour=discord.Colour(ROLE_COLOURS[role]), position=pos)
        else:
            await guild.create_role(name=role, colour=discord.Colour(ROLE_COLOURS[role]))
            await discord.utils.get(guild.roles, name=role).edit(colour=discord.Colour(ROLE_COLOURS[role]), position=pos)
    

if __name__ == "__main__":
    main()
