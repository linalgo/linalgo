"""Command line utilities."""
import typer
import sys
import subprocess

app = typer.Typer()
hub_app = typer.Typer()
app.add_typer(hub_app, name="hub")

@hub_app.command()
def runserver():
    """Launch the annotation server locally."""
    try:
        # Check if linhub is installed
        import linhub
    except ImportError:
        print("Error: linalgo[hub] is not installed. Please install it using:")
        print("pip install linalgo[hub]")
        sys.exit(1)

    # Run the linhub server
    try:
        subprocess.run(["linhub", "runserver"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running linhub server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    app()
