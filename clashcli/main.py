from os                      import getenv
from clashcli                import __version__
from clashcli.commands.clans import clan_typer
from dotenv                  import load_dotenv
from typer                   import Typer, Context





typer = Typer(add_completion = False)
typer.add_typer(clan_typer)

@typer.command()
def version():
    print(__version__)

@typer.callback()
def callback(ctx: Context):
    load_dotenv()
    
    ctx.obj = {}
    ctx.obj["API_KEY"] = getenv("API_KEY")


def main():
    typer()