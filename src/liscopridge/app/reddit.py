import re
from sys import stdout
from typing import Callable
from typing import Dict
from typing import Tuple

import bottle  # type: ignore [import]
import click
from lxml import etree  # type: ignore [import]

from .. import cache

xml_parser = etree.XMLParser(
    attribute_defaults=False,
    dtd_validation=False,
    load_dtd=False,
    no_network=True,
    ns_clean=False,
    recover=False,
    remove_blank_text=False,
    remove_comments=False,
    remove_pis=False,
    strip_cdata=False,
    resolve_entities=False,
    huge_tree=False,
    compact=True,
    collect_ids=False,
)


def subreddit_atom_minscore(subreddit: str, min_score: int) -> bytes:
    atom, json = fetch_subreddit(subreddit)
    details_by_id = {
        child['data']['name']: child['data']
        for child in json['data']['children']
    }

    def has_min_score(entry):
        id_el = entry.find('{http://www.w3.org/2005/Atom}id')
        if id_el is not None:
            i = id_el.text
            if i is not None and len(i) and i in details_by_id:
                details = details_by_id[i]
                if 'score' in details:
                    return details['score'] >= min_score

        return False

    filter_atom_entries(atom, has_min_score)
    return etree.tostring(atom, encoding='UTF-8', xml_declaration=True)


def fetch_subreddit(subreddit: str) -> Tuple[etree.Element, Dict]:
    subreddit_name_validate(subreddit)

    with cache.CachedSession('reddit', expire_after=900) as s:
        s.headers['User-Agent'] = 'liscopridge/1'

        r_atom = s.get(
            f"https://www.reddit.com/r/{subreddit}/top/.rss",
            params={'limit': '100', 'sort': 'top', 't': 'week'})
        r_atom.raise_for_status()

        r_json = s.get(
            f"https://www.reddit.com/r/{subreddit}/top.json",
            params={'limit': '100', 'raw_json': '1', 'sort': 'top', 't': 'week'})
        r_json.raise_for_status()

        return etree.fromstring(r_atom.content, xml_parser), r_json.json()


def subreddit_name_validate(subreddit: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", subreddit):
        bottle.abort(400, "malformed share uri")


def filter_atom_entries(atom: etree.Element, f: Callable) -> None:
    remove = [e for e in atom.iterchildren('{http://www.w3.org/2005/Atom}entry')
              if not f(e)]
    for e in remove:
        atom.remove(e)


@click.group()
def cli():
    pass


@cli.command('subreddit_atom_minscore')
@click.argument('subreddit', required=True, type=str)
@click.argument('min_score', required=True, type=int)
def cli_subreddit_atom_minscore(subreddit, min_score):
    stdout.buffer.write(subreddit_atom_minscore(subreddit, min_score))


if __name__ == "__main__":
    cli()
