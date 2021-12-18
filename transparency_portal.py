from app import app, db
import engine
import get_cheques
import yield_snapshot
from app.models import User, Proposal


@app.cli.command()
def scheduled():
    engine.main()
    get_cheques.main()


@app.cli.command("make_yield_snapshot")
def make_yield_snapshot():
    yield_snapshot.main()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Proposal': Proposal}