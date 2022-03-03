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
    # Will be called every Sunday at 12:04 UTC from a crontab task

@app.cli.command()
def start_cly_payout():
    engine.start_celery_payout()
    # Will be called every Friday at 12:00 UTC from a crontab task

@app.cli.command("make_yield_snapshot")
def make_yield_snapshot():
    yield_snapshot.main()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Proposal': Proposal, 'Users': Users}