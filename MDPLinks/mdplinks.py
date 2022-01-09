'''Clase modelo para los enlaces'''
from typing import Any, Dict, NamedTuple, List
from mdplinks import DB_READ_ERROR, TAG_ERROR, ID_ERROR
from datetime import datetime, timezone

from mdplinks.database import DatabaseHandler

class Link(NamedTuple):
    Link: Dict[str, Any]
    error: int

class LinkController:
    def __init__(self, db_path: str) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add_link(self, url: str, tags: str, title: str='') -> Link:
        '''Agrega un link nuevo a la base de datos'''
        url_text = url
        title_text =""
        if title != "":
            title_text = title

        tags = tags.lower()
        tagList = tags.split(',')
        now = datetime.now(timezone.utc)
        datefmt = now.isoformat(timespec="milliseconds")    
        link = {
            "Url": url_text,
            "Title": title_text,
            "Tags": tagList,
            "CreatedAt": datefmt
        }
        punct = ''' "'¡!¿?.;:-()'''
        for char in tags:                   #agregar a una función checkTags
            if char in punct:
                return Link(link, TAG_ERROR)                     #retorna error por signos de puntuación
        read = self._db_handler.read_links()             #leer link desde DB, llamando al handler
        if read.error == DB_READ_ERROR:
            return Link(link, read.error)
        read.links.append(link)                          #agrega nuevo link a la lista
        write = self._db_handler.write_links(read.links) #actualiza la DB
        return Link(link, write.error)                   #retorna instancia del Link actual

    def get_all_links(self) -> List[Dict[str, Any]]:
        '''Obtiene todos los links de la base de datos'''
        read = self._db_handler.read_links()
        return read.links

    def update_link(self, given_url: str, given_tags: str = "", given_title: str = "") -> Link:        
        read = self._db_handler.read_links()        
        for link in read.links:            
            if link['Url'] == given_url:
                if given_tags != "":
                    tags = given_tags.lower()
                    punct = ''' "'¡!¿?.;:-()'''
                    for char in tags:                   #agregar a una función checkTags
                        if char in punct:
                            return Link(link, TAG_ERROR)                    
                    tagList = tags.split(',')
                    link['Tags'] = tagList
                    
                if given_title != "":
                    link['Title'] = given_title
                write = self._db_handler.write_links(read.links)
                return Link(link, write.error)            
        return Link(link, ID_ERROR)
        
