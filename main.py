from typing import Final, Dict
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from hangman import Hangman  
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)
hangman_sessions: Dict[str, Hangman] = {}

async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('no message here...')
        return
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    try:
        response: str = await get_response(user_message)
        if response :  
            await (message.author.send(response) if is_private else message.channel.send(response))
    except Exception as e:
        print(e)

@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)
    print(f'[{channel}] {username} : {user_message}')
    
    if 'hangman' in user_message.lower():
        if channel not in hangman_sessions:
            hangman_sessions[channel] = Hangman()
            await message.channel.send(f'Starting a new game of Hangman! {hangman_sessions[channel].display_word()}')
        else:
            await message.channel.send(f'A game is already in progress. {hangman_sessions[channel].display_word()}')
        return
    
    if channel in hangman_sessions:
        if len(user_message) == 1 and user_message.isalpha():
            response = hangman_sessions[channel].guess(user_message.lower())
            await message.channel.send(response)
            if 'won' in response or 'lost' in response:
                del hangman_sessions[channel]
        else:
            await message.channel.send('Please guess one letter at a time.')
        return
    
    await send_message(message, user_message)

def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()