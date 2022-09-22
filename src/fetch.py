# DEPENDENCIES =================================================================
import re
import json
import requests

from PIL import Image
from io import BytesIO
from pathlib import Path
from bs4 import BeautifulSoup
from operator import itemgetter
from typing import Generator, Tuple, Callable


# CONSTANTS ====================================================================
# . URL
BASE_URL = 'https://onepiecechapters.com'
CHAPTERS_URL = '/mangas/5/one-piece'

# . PATTERNS
CHAPTER_NUMBER = re.compile(r'One Piece Chapter (\d+)')

# . SELECTORS
CHAPTER = 'block border border-border bg-card mb-3 p-3 rounded'

# . PATHS
CHAPTERS_JSON = Path(__file__).parent / 'data' / 'chapters.json'

# . MISCELLANEOUS
CHAPTER_OFFSET = 4

# FUNCTIONS ====================================================================
get_href: Callable = itemgetter(2)


def fetch_soup(url):
    with requests.get(url) as resp:
        return BeautifulSoup(resp.content, 'html.parser')


def fetch_chapters() -> Generator[Tuple[str, str, str], None, None]:
    '''
    Retrieve all chapter numbers, titles, and hrefs for One Piece.
    '''
    # GET chapters HTML
    soup = fetch_soup(BASE_URL + CHAPTERS_URL)

    # Parse HTML, retrieving:
    # . Chapter number
    # . Title
    # . href
    chapters = soup.find_all('a', href = True, class_ = CHAPTER)
    for chapter in chapters:
        descriptors = chapter.get_text().strip().split('\n')

        # Not all chapter entires have a title
        if len(descriptors) == 1:
            chapter_number = descriptors[0]
            title = None
        elif len(descriptors) == 2:
            chapter_number, title = descriptors

        chapter_number = CHAPTER_NUMBER.match(chapter_number).group(1)
        yield (chapter_number, title, chapter['href']) 


def extract_chapter(chapter_number: int):
    with CHAPTERS_JSON.open('r') as f:
        chapters = json.load(f)

    index = (len(chapters) - chapter_number) - CHAPTER_OFFSET
    href = get_href(chapters[index])

    soup = fetch_soup(BASE_URL + href)
    yield from collect_chapter_pages(soup)


def collect_chapter_pages(chapter_html: BeautifulSoup):
    for page in chapter_html.find_all('picture'):
        with requests.get(page.img['src']) as resp:
            yield Image.open(BytesIO(resp.content)).convert("RGB")