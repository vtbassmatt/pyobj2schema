'Convert a Python object into a relational schema.'
import logging

logger = logging.getLogger(__name__)

def convert(object):
    tables = {}

    if isinstance(object, dict):
        _convert_dict(object, tables)
    elif isinstance(object, list):
        _convert_list(object, tables)
    else:
        raise NotImplementedError('only dicts are supported')

    return tables


def produce_schema(tables):
    sql = []
    for table_name, schema in tables.items():
        cols = [f"{k} {v}" for k, v in schema.items()]
        sql.append(f'CREATE TABLE {table_name} ({", ".join(cols)})')
    return ";\n".join(sql) + ';'


class RedefineKeyError(RuntimeError):
    pass


def _convert_list(object, tables, name=None):
    assert isinstance(object, list)

    if name:
        table_name = name
    else:
        table_name = 'objects'

    if table_name not in tables:
        logger.info(f"creating table {table_name}")
        tables[table_name] = {
            'id': 'INTEGER PRIMARY KEY',
        }
        if name:
            # if this is not the outer-most object,
            # then it's an ordered array and we need
            # to track that
            tables[table_name]['_order'] = 'INTEGER'
    
    # for now, assume that the first item is representative
    if len(object) > 0:
        first = object[0]
        if _handle_scalar('data', first, tables[table_name]):
            pass
        elif isinstance(first, dict):
            if '__name' not in first:
                first_prime = { '__name': table_name }
                first_prime.update(first)
                first = first_prime
            _convert_dict(first, tables)
        elif isinstance(first, list):
            # TODO: handle lists
            pass
        else:
            raise NotImplementedError(f'items in {table_name} are not in a format we understand')
    
    return table_name


def _convert_dict(object, tables):
    assert isinstance(object, dict)

    table_name = object.get('__name', 'object')
    if table_name not in tables:
        logger.info(f"creating table {table_name}")
        tables[table_name] = {'id': 'INTEGER PRIMARY KEY' }

    for k, v in object.items():
        if k.startswith('__'):
            continue

        if k in tables[table_name]:
            raise RedefineKeyError(k)

        if _handle_scalar(k, v, tables[table_name]):
            pass
        elif isinstance(v, dict):
            if '__name' not in v:
                v_prime = { '__name': k }
                v_prime.update(v)
                v = v_prime
            sub_table_name = _convert_dict(v, tables)
            tables[sub_table_name][f"{table_name}_id"] = f"FOREIGN KEY {table_name}.id"
        elif isinstance(v, list):
            # TODO: handle lists
            pass
        else:
            raise NotImplementedError(f'item at {k} is not a format we understand')
    
    return table_name


def _handle_scalar(key, value, table):
    if isinstance(value, bool):
        table[key] = "BOOLEAN"
    elif isinstance(value, int):
        table[key] = "INTEGER"
    elif isinstance(value, float):
        table[key] = "REAL"
    elif isinstance(value, str):
        table[key] = "TEXT"
    else:
        return False
    
    return True


if __name__ == '__main__':
    from pprint import pprint

    example1 = {
        '__name': 'example1',
        'foo': 'is a string',
        'bar': 42,
        'zab': [ 'a', 'b', 'c' ],
        'tab': {
            'bongo': 'boingo',
        },
    }
    result1 = convert(example1)

    print("-- example 1 -- ")
    print("Original object:")
    pprint(example1)
    print("Resulting schema:")
    print(produce_schema(result1))

    example2 = {
     "__name": "card",
     # "id":"0000579f-7b35-4ed3-b44c-db2a538066fe",
     "oracle_id": "44623693-51d6-49ad-8cd7-140505caf02f",
     # "multiverse_ids":[109722],
     "mtgo_id": 25527,
     # "mtgo_foil_id":25528,
     # "tcgplayer_id":14240,
     # "cardmarket_id":13850,
     # "name":"Fury Sliver",
     # "lang":"en",
     # "released_at":"2006-10-06",
     # "uri":"https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe",
     # "scryfall_uri":"https://scryfall.com/card/tsp/157/fury-sliver?utm_source=api",
     # "layout":"normal",
     # "highres_image":true,
     # "image_status":"highres_scan",
     "image_uris": {
          "small": "https://c1.scryfall.com/file/scryfall-cards/small/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
          "normal": "https://c1.scryfall.com/file/scryfall-cards/normal/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
          "large": "https://c1.scryfall.com/file/scryfall-cards/large/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
          "png": "https://c1.scryfall.com/file/scryfall-cards/png/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.png?1562894979",
          "art_crop": "https://c1.scryfall.com/file/scryfall-cards/art_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979",
          "border_crop": "https://c1.scryfall.com/file/scryfall-cards/border_crop/front/0/0/0000579f-7b35-4ed3-b44c-db2a538066fe.jpg?1562894979"
     },
     # "mana_cost":"{5}{R}",
     "cmc": 6.0,
     # "type_line":"Creature — Sliver",
     # "oracle_text":"All Sliver creatures have double strike.",
     # "power":"3",
     # "toughness":"3",
     "colors": ["R"],
     # "color_identity":["R"],
     # "keywords":[],
     # "legalities":{
     #      "standard":"not_legal",
     #      "future":"not_legal",
     #      "historic":"not_legal",
     #      "gladiator":"not_legal",
     #      "pioneer":"not_legal",
     #      "modern":"legal",
     #      "legacy":"legal",
     #      "pauper":"not_legal",
     #      "vintage":"legal",
     #      "penny":"legal",
     #      "commander":"legal",
     #      "brawl":"not_legal",
     #      "duel":"legal",
     #      "oldschool":"not_legal",
     #      "premodern":"not_legal"
     # },
     # "games": ["paper","mtgo"],
    "reserved": False,
     # "foil":true,
     # "nonfoil":true,
     # "oversized":false,
     # "promo":false,
     # "reprint":false,
     # "variation":false,
     # "set_id":"c1d109bc-ffd8-428f-8d7d-3f8d7e648046",
     # "set":"tsp",
     # "set_name":"Time Spiral",
     # "set_type":"expansion",
     # "set_uri":"https://api.scryfall.com/sets/c1d109bc-ffd8-428f-8d7d-3f8d7e648046",
     # "set_search_uri":"https://api.scryfall.com/cards/search?order=set\u0026q=e%3Atsp\u0026unique=prints",
     # "scryfall_set_uri":"https://scryfall.com/sets/tsp?utm_source=api",
     # "rulings_uri":"https://api.scryfall.com/cards/0000579f-7b35-4ed3-b44c-db2a538066fe/rulings",
     # "prints_search_uri":"https://api.scryfall.com/cards/search?order=released\u0026q=oracleid%3A44623693-51d6-49ad-8cd7-140505caf02f\u0026unique=prints",
     # "collector_number":"157",
     # "digital":false,
     # "rarity":"uncommon",
     # "flavor_text":"\"A rift opened, and our arrows were abruptly stilled. To move was to push the world. But the sliver's claw still twitched, red wounds appeared in Thed's chest, and ribbons of blood hung in the air.\"\n—Adom Capashen, Benalish hero",
     # "card_back_id":"0aeebaf5-8c7d-4636-9e82-8c27447861f7",
     # "artist":"Paolo Parente",
     # "artist_ids":["d48dd097-720d-476a-8722-6a02854ae28b"],
     # "illustration_id":"2fcca987-364c-4738-a75b-099d8a26d614",
     # "border_color":"black",
     # "frame":"2003",
     # "full_art":false,
     # "textless":false,
     # "booster":true,
     # "story_spotlight":false,
     # "edhrec_rank":5181,
     "prices": {
          "usd": "1.01",
          "usd_foil": "5.68",
          "eur": "0.10",
          "eur_foil": "1.00",
          "tix": "0.03"
     },
     # "related_uris":{
     #      "gatherer":"https://gatherer.wizards.com/Pages/Card/Details.aspx?multiverseid=109722",
     #      "tcgplayer_infinite_articles":"https://infinite.tcgplayer.com/search?contentMode=article\u0026game=magic\u0026partner=scryfall\u0026q=Fury+Sliver\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall",
     #      "tcgplayer_infinite_decks":"https://infinite.tcgplayer.com/search?contentMode=deck\u0026game=magic\u0026partner=scryfall\u0026q=Fury+Sliver\u0026utm_campaign=affiliate\u0026utm_medium=api\u0026utm_source=scryfall",
     #      "edhrec":"https://edhrec.com/route/?cc=Fury+Sliver",
     #      "mtgtop8":"https://mtgtop8.com/search?MD_check=1\u0026SB_check=1\u0026cards=Fury+Sliver"
     # }
    }
    result2 = convert(example2)
    print("-- example 2 -- ")
    print("Original object:")
    pprint(example2)
    print("Resulting schema:")
    print(produce_schema(result2))

    example3 = [
        {
            'foo': 'is a string',
            'bar': 42,
        },
    ]
    result3 = convert(example3)

    print("-- example 3 -- ")
    print("Original object:")
    pprint(example3)
    print("Resulting schema:")
    print(produce_schema(result3))
