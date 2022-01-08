"""This module provides the MDPLinks CLI."""
# mdplinks/cli.py

from typing import Optional
import os
import typer

from mdplinks import __app_name__, __version__
app = typer.Typer()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version", #nombres de linea de comando para version
        "-v",
        help="Show the application's version and exit.", #msg de ayuda
        callback=_version_callback, #ejecutar esta funcion tras correr la opción
        is_eager=True, #eager indica que esta opción tiene precedencia sobre otros comandos
    )
) -> None:
    return

@app.command()
def init(
    db_path: str = typer.Option(
        "mdplinks/db/",
        "--db-path",
        "-db",
        prompt="Database location?"
    ),
) -> None:
    if os.path.isdir(db_path):
        if not os.listdir(db_path):            
            typer.secho(f"Database path set to {db_path}. Created the database.", fg=typer.colors.YELLOW)
            #crear db!!        
            with open(db_path+"database.json", "w") as f:
                f.write("[]")
        else:
            typer.secho(f"Error: The database already exists!", fg=typer.colors.RED)
    else:
        typer.secho(f"Error: The given directory does not exist!", fg=typer.colors.RED)

'''@app.command()
def create_link(url: str, title: str = ""):'''
