import os
import sys
import traceback
from pathlib import Path
from typing import List

from whaaaaat import prompt, Separator

from modules import console
from modules import database
from modules import resume
from modules import settings
from modules.codec import MKCodec
from modules.commandline import parse
from modules.composition import compose_menu
from modules.console import vinput
from modules.conversions import list_to_file
from modules.database import models
from modules.database.models.manga.download import selective_download
from modules.manager import HtmlManager, MangaManager
from modules.static import Const
from modules.styles import style
from modules.ui import colorize, Loader


def search():
    search_answer = vinput('Enter here to search:')

    search = search_answer['search']
    url = codec.search_prefix + search
    while True:
        codec.search(url)

        # mutate options to include page routing
        choices: List = codec.search_result[:]
        if codec.previous_page_exists():
            choices.insert(0, 'PREVIOUS')
        if codec.next_page_exists():
            choices.append('NEXT')

        search_question = {
            'type': 'list',
            'name': 'search',
            'message': 'choose',
            'choices': choices
        }

        search_answer = prompt(search_question)

        if search_answer['search'] == 'PREVIOUS':
            url = codec.get_page(codec.current_page - 1)
            continue
        elif search_answer['search'] == 'NEXT':
            url = codec.get_page(codec.current_page + 1)
            continue
        else:
            for result in codec.search_result:
                if result['name'] == search_answer['search']:
                    return models.Manga(result['name'], result['href'])


def direct():
    answer = vinput('Enter the url: ')

    parsed_manga, chapters = models.Manga('', answer).parse()

    return parsed_manga, chapters


def download_link(manga: models.Manga, chapters=None):
    if not chapters:
        manga, chapters = manga.parse()

    question = {
        'type': 'checkbox',
        'name': 'chapters',
        'message': 'Select chapters to download',
        'choices': [{'name': i.title} for i in chapters],
    }

    answers = prompt(question)

    if not answers['chapters']:
        return

    selected = []
    for chapter in chapters:
        if chapter.title in answers['chapters']:
            selected.append(chapter)

    selective_download(manga, chapters, selected)


def check_files():
    """
    Checks for existence of necessary files and folders
    """
    if not os.path.exists(Const.MangaSavePath):
        os.mkdir(Const.MangaSavePath)

    if not os.path.exists(Const.StyleSaveFile):
        list_to_file(style, Const.StyleSaveFile)


def continue_downloads():
    manga, unfinished = resume.get()

    if len(unfinished) <= 0:
        return

    # user prompt
    print(
        f'Download of {len(unfinished)} {"chapter" if len(unfinished) == 1 else "chapters"} from "{manga.title}" unfinished.')
    should_resume = console.confirm('Would you like to resume?', default=True)

    if not should_resume:
        # remove all from database and exit
        database.meta.downloads_left.purge()
        return

    # start download
    manga, chapters = manga.parse()
    selective_download(manga, chapters, [models.Chapter.fromdict(chapter) for chapter in unfinished])


if __name__ == '__main__':
    # set working directory
    os.chdir(str(Path(sys.executable if getattr(sys, 'frozen', False) else __file__).parent))

    # PLAYGROUND

    # from modules.database.models import DictClass
    #
    # class ex(DictClass):
    #     def __init__(self, a, b):
    #         self.a = a,
    #         self.b = b
    #
    # input()
    # END

    continue_downloads()

    codec: MKCodec = MKCodec()
    manga_manager: MangaManager = MangaManager()
    html_manager: HtmlManager = HtmlManager()

    check_files()

    # commandline argument parse
    skip_menu, args = parse()

    while True:
        menuoption = {}
        if not skip_menu:
            mainmenu = {
                'type': 'list',
                'name': 'menu',
                'message': 'what do you wanna do?',
                'choices': [
                    'Search for manga',
                    'Open manga using direct url',
                    'View the manga',
                    Separator('-'),
                    'Compose',
                    'Settings',
                    'Exit'
                ],
                'filter': lambda val: mainmenu['choices'].index(val)
            }

            menuoption = prompt(mainmenu)
        else:
            if args.view:
                menuoption['menu'] = 2

        if menuoption['menu'] == 0:
            try:
                download_link(search())
            except Exception:
                traceback.print_exc()
        elif menuoption['menu'] == 1:
            try:
                manga, chapters = direct()
                download_link(manga, chapters)
            except Exception:
                traceback.print_exc()
        elif menuoption['menu'] == 2:
            # generate manga tree
            with Loader('Generating tree'):
                manga_manager.generate_tree()

            # generate html pages using the tree
            with Loader('Generating html files.'):
                html_manager.generate_web(manga_manager.tree)

            if html_manager.open():
                break
        elif menuoption['menu'] == 4:
            compose_menu()
        elif menuoption['menu'] == 5:
            settings.change()
        elif menuoption['menu'] == 6:
            break
        else:
            print(colorize.red('Pick a valid choice'))
