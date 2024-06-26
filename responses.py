from random import choice, randint
import aiohttp


async def get_joke() -> str:
    joke_url = 'https://official-joke-api.appspot.com/random_joke'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(joke_url) as response:
                if response.status == 200:
                    joke_data = await response.json()
                    setup = joke_data.get('setup', '')
                    punchline = joke_data.get('punchline', '')
                    return f"{setup}\n\n{punchline}"
                else:
                    return 'Failed to fetch joke. Try again later.'
    except Exception as e:
        print(f'Error fetching joke: {e}')
        return 'Failed to fetch joke. Try again later.'

async def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'silence'
    elif 'hello' in lowered:
        return 'hi hi'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1, 6)}'
    elif 'joke' in lowered:
        return await get_joke()  
    else:
        return ''