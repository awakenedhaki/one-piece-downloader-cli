# DEPENDENCIES =================================================================
import json
import click
import pprint

from pathlib import Path
from fetch import (
    fetch_chapters,
    extract_chapter,
    CHAPTERS_JSON
)


# HELPERS ======================================================================
def update_chapters_json() -> None:
    with CHAPTERS_JSON.open(mode = 'w') as f:
        json.dump(list(fetch_chapters()), f)


def save_chapter_as_pdf(pages, chapter_number):
    first_page = next(pages)
    first_page.save(f'{chapter_number}.pdf', 
                    save_all = True,
                    append_images = tuple(pages))


# CLI ==========================================================================
@click.command()
@click.option('--chapter', type = click.INT)
@click.option('--update', is_flag = True)
def download(chapter, update):
    if update:
        update_chapters_json(
            fetch_chapters()
            )
    chapter_pages = extract_chapter(chapter)
    save_chapter_as_pdf(chapter_pages, chapter)


@click.command()
@click.option('--top', type = click.INT)
def list(top):
    with CHAPTERS_JSON.open(mode = 'r') as f:
        chapters = json.load(f)
    click.echo(pprint.pprint(chapters[:top]))


@click.group()
def main():
    pass


main.add_command(download)
main.add_command(list)


if __name__ == '__main__':
    main()