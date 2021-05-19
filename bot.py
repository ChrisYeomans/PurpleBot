import discord

TEST = True
ROLE_MESSAGE_ID = -1
EMOJI_ROLE_DICT = {"👍": "test"}
ROLE_COLOURS = {"test": 0xffffff}

def main():
    TOKEN = input()
    intents = discord.Intents.default()
    intents.members = True 

    client = discord.Client(intents=intents)


    @client.event
    async def on_ready():
        global ROLE_MESSAGE_ID
        for g in client.guilds:
            if TEST or "purple" in g.name.lower():
                for tc in g.text_channels:
                    if tc.name == "roles":
                        async for message in tc.history(limit=10):
                            if message.author == client.user and "role" in message.content.lower():
                                ROLE_MESSAGE_ID = message.id
        print("Bot Ready")
        print(ROLE_MESSAGE_ID)
    
    @client.event
    async def on_raw_reaction_add(payload):
        user = payload.member
        if user != client.user:
            emoji = str(payload.emoji)
            if emoji in EMOJI_ROLE_DICT:
                await user.add_roles(discord.utils.get(user.guild.roles, name=EMOJI_ROLE_DICT[emoji]))

    @client.event
    async def on_raw_reaction_remove(payload):
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
        if message.content == "setup_reaction_message" and message.author.guild_permissions.administrator:
            await setup_reaction_message(message)
            await message.delete()


    client.run(TOKEN)

async def setup_reaction_message(tc):
    # Build message
    
    reaction_message = f"React to the following to get the relevant role\n"
    for i in EMOJI_ROLE_DICT:
        reaction_message += f"{i} {EMOJI_ROLE_DICT[i]}\n"

    # Send message and add reactions
    m = await tc.send(reaction_message)
    for i in EMOJI_ROLE_DICT:
        await m.add_reaction(i)

async def create_colour_roles(guild):
    for role in ROLE_COLOURS:
        await guild.create_role(name="role", colour=discord.Colour(ROLE_COLOURS[role]))
    

if __name__ == "__main__":
    main()
