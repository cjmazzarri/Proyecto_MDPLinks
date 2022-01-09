import configparser
import json
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from mdplinks import DB_READ_ERROR, DB_WRITE_ERROR, JSON_ERROR, SUCCESS

class DBResponse(NamedTuple):
    links: List[Dict[str, Any]] #lista de diccionarios
    error: int

class DatabaseHandler:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def read_links(self) -> DBResponse:
        try:
            with open(self._db_path+"database.json", "r") as db:        
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:  # Catch wrong JSON format
                    return DBResponse([], JSON_ERROR)
        except OSError:  # Catch file IO problems            
            return DBResponse([], DB_READ_ERROR)

    def write_links(self, links: List[Dict[str, Any]]) -> DBResponse:
        try:
            with open(self._db_path+"database.json", "w") as db:
            #with open("mdplinks/db/database.json", "w") as db:
                json.dump(links, db, indent=4)
            return DBResponse(links, SUCCESS)
        except OSError:  # Catch file IO problems
            return DBResponse(links, DB_WRITE_ERROR)