from app import app
import engine
import get_cheques
import yield_snapshot


@app.cli.command()
def scheduled():
    engine.main()
    get_cheques.main()


@app.cli.command("make_yield_snapshot")
def make_yield_snapshot():
    yield_snapshot.main()
