"""Definitions of readers, i.e. functions interfacing end-user
with readings API.

"""

import shutil
import tempfile
import webbrowser
from readings import Story, Topic, UserResult


def boolean_user_input(text:str) -> bool:
    """Prompt user for given yes/no question. Default is yes."""
    return 'n' not in input("<"+text+" [Y/n]>").strip().lower()


def term_reader(story:Story, *, interactive:bool=True):
    """Print given story in terminal."""
    WIDTH = shutil.get_terminal_size((80, 20)).columns
    print('#' * WIDTH)
    print(story.topic.text)
    print(' -' * (WIDTH//6))
    print('Proposed by ' + story.topic.author + ' the ' + story.sub_date)
    print('#' * WIDTH)
    print()
    print(story.text)
    print()
    print()
    author = 'Written by ' + story.author + ' the ' + story.sub_date + ' '
    print(author + '#' * (WIDTH - len(author)))
    print("Thanks the authors at " + story.permalink)
    if interactive:
        result = UserResult(isread=boolean_user_input('Mark as read ?'))
        return boolean_user_input('Next ?') and result
    return True


def browser_reader(story:Story):
    """Open story in browser"""
    with tempfile.NamedTemporaryFile(delete=False) as fd:
        fd.write(story.html)
    webbrowser.open(fd.name)
    return 'n' not in input("<Next story ?[Y/n]>").strip().lower()


