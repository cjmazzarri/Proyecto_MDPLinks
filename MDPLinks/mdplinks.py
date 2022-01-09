'''Clase modelo para los enlaces'''
from os import write
from pathlib import Path
from typing import Any, Dict, NamedTuple, List
from mdplinks import DB_READ_ERROR
from datetime import datetime, timezone

from mdplinks.database import DatabaseHandler

class Link(NamedTuple):
    Link: Dict[str, Any]
    error: int

class LinkController:
    def __init__(self, db_path: str) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add_link(self, url: str, tags: str, title: str='') -> Link:
        '''Adds a new link to the database'''
        url_text = url
        title_text =""
        if title != "":
            title_text = title
        tagList = [tags.split(',')]
        now = datetime.now(timezone.utc)
        datefmt = now.isoformat(timespec="milliseconds")    
        link = {
            "Url": url_text,
            "Title": title_text,
            "Tags": tagList,
            "CreatedAt": datefmt
        }
        read = self._db_handler.read_links()             #leer link desde DB, llamando al handler
        if read.error == DB_READ_ERROR:
            return Link(link, read.error)
        read.links.append(link)                          #agrega nuevo link a la lista
        write = self._db_handler.write_links(read.links) #actualiza la DB
        return Link(link, write.error)                   #retorna instancia del Link actual

    
