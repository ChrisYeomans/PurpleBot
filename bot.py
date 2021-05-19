import discord, asyncio

ROLE_MESSAGE_ID = -1
EMOJI_ROLE_DICT = {"👍": "test"}

def main():
    TOKEN = input()
    client = discord.Client()

    @client.event
    async def on_ready():
        global ROLE_MESSAGE_ID
        for tc in client.guilds[0].text_channels:
            if tc.name == "roles":
                async for message in tc.history(limit=10):
                    if message.author == client.user and "role" in message.content.lower():
                        ROLE_MESSAGE_ID = message.id
        print("Bot Ready")
        print(ROLE_MESSAGE_ID)
    
    @client.event
    async def on_raw_reaction_add(payload):
        user = payload.member
        emoji = str(payload.emoji)
        if emoji in EMOJI_ROLE_DICT:
            await user.add_roles([EMOJI_ROLE_DICT[emoji]])




    @client.event
    async def on_guild_join(guild):
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

    



if __name__ == "__main__":
    main()
