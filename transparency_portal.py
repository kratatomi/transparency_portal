from app import app, db
import engine
import voting_platform
import yield_snapshot
from app.models import User, Proposal, Users


@app.cli.command()
def scheduled():
    engine.main()
    voting_platform.main()

@app.cli.command()
def start_cly_staking():
    engine.start_celery_stake()

@app.cli.command()
def start_cly_payout():
    engine.start_celery_payout()

@app.cli.command("make_yield_snapshot")
def make_yield_snapshot():
    yield_snapshot.main()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Proposal': Proposal, 'Users': Users}