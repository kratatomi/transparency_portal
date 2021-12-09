from app import app
import engine
import get_cheques

@app.cli.command()
def scheduled():
    engine.main()
    get_cheques.main()