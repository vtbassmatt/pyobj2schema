import decimal
from sqlalchemy import Numeric, Date


_example0 = {
    '__name': 'example0',
    'foo': 'stringy',
    'bar': 42,
    'isit': True,
    'isntit': False,
    'dewey': decimal.Decimal(0.5),
}

_example1 = {
    '__name': 'example1',
    '__id': 'bar',  # define the ID column
    'foo': 'is a string',
    'bar': 42,
    'zab': [ 'a', 'b', 'c' ],
    'tab': {
        'bongo': 'boingo',
    },
    'nest': [
        [ 'double-nest-1', 'double-nest-2' ],
    ],
}

# this example courtesy https://scryfall.com
_example2 = {
    "__name": "card",
    "id": "0000579f-7b35-4ed3-b44c-db2a538066fe",
    "oracle_id": "44623693-51d6-49ad-8cd7-140505caf02f",
    "multiverse_ids": [ 109722 ],
    "mtgo_id": 25527,
    "mtgo_foil_id": 25528,
    "tcgplayer_id": 14240,
    "cardmarket_id": 13850,
    "name": "Fury Sliver",
    "lang": "en",
    "released_at": "2006-10-06",
    "uri": "https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe",
    "scryfall_uri": "https://scryfall.com/card/tsp/157/fury-sliver?utm_source=api",
    "layout": "normal",
    "highres_image": True,
    "image_status": "highres_scan",
    "image_uris": {
        "small": "https://c1.scryfall.com/file/scryfall-cards/small/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "normal": "https://c1.scryfall.com/file/scryfall-cards/normal/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "large": "https://c1.scryfall.com/file/scryfall-cards/large/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "png": "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
        "art_crop": "https://c1.scryfall.com/file/scryfall-cards/art_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
        "border_crop": "https://c1.scryfall.com/file/scryfall-cards/border_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979"
    },
    "mana_cost": "{5}{R}",
    "cmc": 6.0,
    "type_line": "Creature — Sliver",
    "oracle_text": "All Sliver creatures have double strike.",
    "power": "3",
    "toughness": "3",
    "colors": [ "R" ],
    "color_identity": [ "R" ],
    "keywords": [],
    "legalities": {
         "standard": "not_legal",
         "future": "not_legal",
         "historic": "not_legal",
         "gladiator": "not_legal",
         "pioneer": "not_legal",
         "modern": "legal",
         "legacy": "legal",
         "pauper": "not_legal",
         "vintage": "legal",
         "penny": "legal",
         "commander": "legal",
         "brawl": "not_legal",
         "duel": "legal",
         "oldschool": "not_legal",
         "premodern": "not_legal"
    },
    "games": [ "paper", "mtgo" ],
    "reserved": False,
    "foil": True,
    "nonfoil": True,
    "oversized": False,
    "promo": False,
    "reprint": False,
    "variation": False,
    "set_id": "c1d109bc-ffd8-428f-8d7d-3f8d7e648046",
    "set": "tsp",
    "set_name": "Time Spiral",
    "set_type": "expansion",
    "set_uri": "https://api.scryfall.com/sets/c1d109bc-ffd8-428f-8d7d-3f8d7e648046",
    "set_search_uri": "https://api.scryfall.com/cards/search?order=set\u0026q=e%3Atsp\u0026unique=prints",
    "scryfall_set_uri": "https://scryfall.com/sets/tsp?utm_source=api",
    "rulings_uri": "https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe/rulings",
    "prints_search_uri": "https://api.scryfall.com/cards/search?order=released\u0026q=oracleid%3A44623693-51d6-49ad-8cd7-140505caf02f\u0026unique=prints",
    "collector_number": "157",
    "digital": False,
    "rarity": "uncommon",
    "flavor_text": "\"A rift opened, and our arrows were abruptly stilled. To move was to push the world. But the sliver's claw still twitched, red wounds appeared in Thed's chest, and ribbons of blood hung in the air.\"\n—Adom Capashen, Benalish hero",
    "card_back_id": "0aeebaf5-8c7d-4636-9e82-8c27447861f7",
    "artist": "Paolo Parente",
    "artist_ids": [ "d48dd097-720d-476a-8722-6a02854ae28b" ],
    "illustration_id": "2fcca987-364c-4738-a75b-099d8a26d614",
    "border_color": "black",
    "frame": "2003",
    "full_art": False,
    "textless": False,
    "booster": True,
    "story_spotlight": False,
    "edhrec_rank": 5181,
    "prices": {
        "usd": "1.01",
        "usd_foil": "5.68",
        "eur": "0.10",
        "eur_foil": "1.00",
        "tix": "0.03"
    },
    "related_uris": {
         "gatherer": "https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=109722",
         "tcgplayer_infinite_articles": "https://infinite.tcgplayer.com/search?contentMode=article\u0026game=magic\u0026partner=scryfall\u0026q=Fury+Sliver\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall",
         "tcgplayer_infinite_decks": "https://infinite.tcgplayer.com/search?contentMode=deck\u0026game=magic\u0026partner=scryfall\u0026q=Fury+Sliver\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall",
         "edhrec": "https://edhrec.com/route/?cc=Fury+Sliver",
         "mtgtop8": "https://mtgtop8.com/search?MD_check=1\u0026SB_check=1\u0026cards=Fury+Sliver"
    }
}
_example2_hints = {
    'card.cmc': {
        'type': Numeric,
    },
    'card.released_at': {
        'type': Date,
    },
    'multiverse_ids': {
        'data_name': 'multiverse_id',
    },
    'games': {
        'data_name': 'game',
    },
    'artist_ids': {
        'data_name': 'artist_id',
    },
}

_example3 = [
    {
        'foo': 'is a string',
        'bar': 42,
    },
    {
        'foo': 'still a string',
        'tab': True,
    },
    {
        'foo': 'this should upconvert',
        'bar': decimal.Decimal(42.5),
    },
]


EXAMPLES = (
#    _example0,
    _example1,
#    (_example2, _example2_hints),
#    _example3,
)


if __name__ == '__main__':
    import logging
    import os

    log_level = os.environ.get('LOGLEVEL', None)
    if log_level:
        numeric_level = getattr(logging, log_level.upper(), None)
        if numeric_level:
            logging.basicConfig(level=numeric_level)
        else:
            logging.warning(f'{log_level} is not a valid log level')
    
    logger = logging.getLogger('examples.py')

    from pprint import pprint
    from sqlalchemy.dialects import sqlite
    from sqlalchemy.schema import CreateTable
    from typing import Tuple

    from pyobj2schema import convert

    for index, example in enumerate(EXAMPLES):
        if isinstance(example, Tuple):
            example, hints = example
        else:
            hints = {}
        result = convert(example, hints)

        print(f"-- example {index} -- ")
        print("Original object:")
        pprint(example)
        print("Resulting schema:")
        for table in result.sorted_tables:
            ct = CreateTable(table)
            print(ct.compile(dialect=sqlite.dialect()))
