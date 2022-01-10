"""This module provides the MDPLinks CLI."""
# mdplinks/cli.py

from typing import Optional, List
import os
from click.termui import prompt
import typer
from pathlib import Path
from datetime import date, timezone, datetime
from babel.dates import format_datetime, get_timezone
import math
import msvcrt as m

from mdplinks import database, ERRORS, mdplinks
from mdplinks import __app_name__, __version__
app = typer.Typer()
DB_PATH = "mdplinks/db/"
tz = get_timezone()

def wait():
    key = m.getch()
    if key == b'q':
        typer.secho('Salida', fg=typer.colors.YELLOW)
        raise typer.Exit()
    return

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
        help="Mostrar la versión de la aplicación.", #msg de ayuda
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
    title: str = typer.Option("", help="Un título para el enlace, si desea agregarlo. Escriba entre comillas dobles \"\" para incluir espacios."),
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
    typer.secho("\nMostrando los enlaces registrados en total ("+str(len(link_list))+"):\n", fg=typer.colors.BRIGHT_GREEN)

    for link in link_list:              #se podría mover esto a una función mostrar() para mejor orden
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
    '''Editar las etiquetas/título de un link'''
    controller = get_controller()
    link, error = controller.update_link(url, tags, title)
    if error:
        typer.secho(f'Error al modificar enlace: "{ERRORS[error]}"', fg=typer.colors.RED)
        raise typer.Exit(1)
    else:
        typer.secho(f'Se modificaron los datos del enlace de url {url}.', fg=typer.colors.BLUE)
    
@app.command(name="tag-search")
def tag_search(
    tag: str = typer.Option("",help="La etiqueta que será usada para consultar links."),
    tags: str = typer.Option("", help="Las etiquetas que se usarán para consultar links, si desea buscar con más de una a la vez."),
    per_page: int = typer.Option(25, help="Cantidad de enlaces a mostrar por página.")

) -> None:
    '''Buscar links por 1 o varias etiquetas. Si no se incluye --tag ni --tags, se mostrará la totalidad de los registros.'''
    controller = get_controller()
    if per_page < 1:
        typer.secho('Error: ¡El modificador --per-page deber ser mayor o igual que 1!', fg=typer.colors.RED)
        raise typer.Exit(1)
    if tag=="" and tags=="":
        get_all_links()
        raise typer.Exit()
    if tag!="":
        link_list = controller.search_by_tag(tag)
        typer.secho(f"Se encontraron {len(link_list)} enlaces encontrados con la etiqueta {tag}.",fg=typer.colors.GREEN)
    else: 
        link_list = controller.search_multitag(tags)
        typer.secho(f"Se encontraron {len(link_list)} enlaces encontrados con las etiquetas {tag}.",fg=typer.colors.GREEN)
    pages = math.ceil(len(link_list)/per_page)
    if len(link_list) > 0:
        page_count = 1 
    else: 
        page_count = 0
    
    typer.secho(f"Mostrando {per_page} enlaces por página.", fg=typer.colors.BLUE)
    typer.secho(f"Página {page_count} de {pages}" ,fg=typer.colors.BRIGHT_YELLOW)
    link_count = 0
    for link in link_list:        
        taglist = ",".join(link['Tags'])
        rawdate = link['CreatedAt']
        datestr = datetime.fromisoformat(rawdate)
        datefmt = format_datetime(datestr, "EEEE, dd 'de' MMMM 'de' YYYY HH:mm:ss:SS ZZ", tzinfo=tz, locale='es') #tzinfo='America/Bogota'
        if link_count == per_page:            
            typer.secho('Presione cualquier tecla para pasar a la siguiente página. Presione la tecla Q para salir.', fg=typer.colors.BRIGHT_BLUE)
            wait()
            page_count+=1
            typer.secho(f"Página {page_count} de {pages}" ,fg=typer.colors.BRIGHT_YELLOW)
            link_count = 0            

        typer.secho(
            f"* Título: {link['Title']}" if link['Title'] != "" else f"* [Sin título]",
            fg=typer.colors.YELLOW)
        typer.secho(f"  URL: {link['Url']}"
                    f"  Etiquetas: {taglist}",
                    fg=typer.colors.YELLOW)
        typer.secho(f"  Fecha y hora de creación: {datefmt}\n", fg=typer.colors.YELLOW)
        link_count+=1
    typer.secho('Fin de los resultados', fg=typer.colors.YELLOW)


    