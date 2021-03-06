from modules.ui import unicode
from modules.ui.colorize import green, red, blue

def title(s):
    return f'{blue("?")} {s}'

def visualize(val) -> str:
    """
    :returns appropriate symbol for the val colorized
    """
    if type(val) == bool:
        if val:
            return green(unicode.CHECK_MARK)
        else:
            return red('X')
    else:
        return val


def format_dict_pair(key, value):
    return f'[{visualize(value)}] {key}'