from typing import Final, Dict, List
import os
from dotenv import load_dotenv
from discord import Intents, Message, File
from discord.ext import commands
import aiohttp
from PIL import Image
from io import BytesIO
from hangman import Hangman  
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
hangman_sessions: Dict[str, Hangman] = {}
GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

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

@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running!')

@bot.event
async def on_message(message: Message) -> None:
    if message.author == bot.user:
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
    await bot.process_commands(message)

async def fetch_image_urls(query: str, count: int = 1) -> List[str]:
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "searchType": "image",
        "q": query,
        "num": count,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(GOOGLE_SEARCH_URL, params=params) as response:
            data = await response.json()
            image_urls = [img['link'] for img in data['items']]
            return image_urls

async def download_image(url: str) -> Image.Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_data = await response.read()
            return Image.open(BytesIO(image_data))

async def combine_images(images: List[Image.Image]) -> Image.Image:
    widths, heights = zip(*(img.size for img in images))
    total_width = sum(widths)
    max_height = max(heights)
    combined_image = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for img in images:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.width
    return combined_image

def resize_image(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    width_ratio = max_width / image.width
    height_ratio = max_height / image.height
    new_size = (int(image.width * width_ratio), int(image.height * height_ratio)) if width_ratio < height_ratio else (int(image.width * height_ratio), int(image.height * height_ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)

@bot.command()
async def combine(ctx, *keywords: str):
    if len(keywords) < 2:
        await ctx.send("Please provide at least two keywords.")
        return

    try:
        image_urls = []
        for keyword in keywords[:2]:
            urls = await fetch_image_urls(keyword)
            image_urls.extend(urls)
        
        images = [await download_image(url) for url in image_urls]
        resized_images = [resize_image(img, 500, 500) for img in images] 
        combined_image = await combine_images(resized_images)

        with BytesIO() as image_binary:
            combined_image.save(image_binary, 'PNG', quality=85)  
            image_binary.seek(0)
            if image_binary.getbuffer().nbytes < 8 * 1024 * 1024:  
                await ctx.send(file=File(fp=image_binary, filename='combined.png'))
            else:
                await ctx.send("The combined image is too large to send.")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
