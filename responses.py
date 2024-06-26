from random import choice, randint

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'silence'
    elif 'hello'  in lowered:
        return 'hi hi'
    elif 'roll dice' in lowered:
        return f'You rolled: {randint(1,6)}'
    else:
        return choice(['I do not understand...',
                       'What?',
                       'no idea what you are saying'])