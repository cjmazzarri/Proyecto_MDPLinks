"""MDPLinks entry point script."""
# MDPLinks/__main__.py

from mdplinks import cli, __app_name__

def main():
    cli.app(prog_name=__app_name__) #llamada a la aplicación typer

if __name__ == "__main__":
    main()