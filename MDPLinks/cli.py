"""This module provides the MDPLinks CLI."""
# mdplinks/cli.py

from typing import Optional, List
import os
from click.termui import prompt
import typer
from pathlib import Path
from datetime import date, timezone, datetime
from babel.dates import format_datetime, get_timezone

from mdplinks import __app_name__, __version__, database, mdplinks, ERRORS
app = typer.Typer()
DB_PATH = "mdplinks/db/"
tz = get_timezone()

def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        typer.echo(DB_PATH)
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
        prompt="Ingrese la ruta para la base de datos: "
    ),
) -> None:
    '''Inicializar la base de datos.'''
    if os.path.isdir(db_path):
        if not os.listdir(db_path):            
            typer.secho(f"Ruta de base de datos configurada como {db_path}. Se creó la base de datos.", fg=typer.colors.YELLOW)
            DB_PATH = db_path
            print("DB_PATH: ",DB_PATH)
            with open(db_path+"database.json", "w") as f:
                f.write("[]")
        else:
            typer.secho(f"Error: ¡La base de datos ya existe!", fg=typer.colors.RED)
    else:
        typer.secho(f"Error: ¡El directorio ingresado no existe!", fg=typer.colors.RED)
    return db_path

def get_controller() -> mdplinks.LinkController:
    if DB_PATH != "":
        return mdplinks.LinkController(DB_PATH)
    else:
        typer.secho('Error: Base de datos no encontrada', fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def add_link(
    title: str = typer.Option(""),
    url: str = typer.Argument(..., help="El enlace de la página web que se desea agregar"),
    tags: str = typer.Option(..., help="Las etiquetas separadas por comas"),
) -> None:
    '''Agregar un nuevo enlace con url, título (opcional) y etiquetas'''
    controller = get_controller()
    link, error = controller.add_link(url, tags, title)
    if error:
        typer.secho(f'Error al agregar enlace: "{ERRORS[error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)
    else:
        typer.secho(f"""Se agregó el enlace: "{link['Url']}" """
                    f"""con las etiquetas {tags}""",
                    fg=typer.colors.YELLOW) if link['Title'] == "" else typer.secho(f"""Se agregó el enlace: "{link['Url']}" """
                    f"con el título: {link['Title']}"
                    f""" y las etiquetas: {tags.lower()}""",
                    fg=typer.colors.YELLOW)

@app.command(name="get-all")
def get_all_links() -> None:
    '''Lista todos los enlaces registrados.'''
    controller = get_controller()
    link_list = controller.get_all_links()
    if len(link_list) == 0:
        typer.secho("No se han agregado registros a la base de datos aún.", fg=typer.colors.RED)
        raise typer.Exit()
    typer.secho("\nEnlaces registrados ("+str(len(link_list))+"):\n", fg=typer.colors.BRIGHT_GREEN)

    for link in link_list:
        taglist = ",".join(link['Tags'])
        rawdate = link['CreatedAt']
        datestr = datetime.fromisoformat(rawdate)
        datefmt = format_datetime(datestr, "EEEE, dd 'de' MMMM 'de' YYYY HH:mm:ss:SS ZZ", tzinfo=tz, locale='es') #tzinfo='America/Bogota'
        
        typer.secho(
            f"* Título: {link['Title']}" if link['Title'] != "" else f"* [Sin título]",
            fg=typer.colors.YELLOW)
        typer.secho(f"  URL: {link['Url']}"
                    f"  Etiquetas: {taglist}",
                    fg=typer.colors.YELLOW)
        typer.secho(f"  Fecha y hora de creación: {datefmt}\n", fg=typer.colors.YELLOW)

@app.command(name="edit-link")
def edit_link(
    url: str = typer.Argument(..., help="El link que desea modificar"),
    title: str = typer.Option("", help="El nuevo título para el link"),
    tags: str = typer.Option("", help="Las nuevas etiquetas para el link")
) -> None:
    """Editar las etiquetas/título de un link"""
    controller = get_controller()
    link, error = controller.update_link(url, tags, title)
    if error:
        typer.secho(f'Error al modificar enlace: "{ERRORS[error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)
    else:
        typer.secho(f'Se modificaron los datos del enlace de url {url}.', fg=typer.colors.BLUE)

