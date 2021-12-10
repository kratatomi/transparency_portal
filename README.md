# transparency_portal
Transparency portal for SmartIndex, a web app based on Flask.

Python version used: 3.8.
For requirements, see requirements.txt file.

All data fetched from the SmartBCH blockchain is stored in the /data folder.
Data is synced every 5 minutes using a cron tab, run crontab -e and insert this line:
*/5 * * * * cd $HOME/transparency_portal && venv/bin/flask scheduled >scheduled.log 2>&1

Updating the list of LAW punks NFTs is very RPC intensive and takes a lot of time, so the command is called manually: 
import engine
engine.update_punks_balance()

For running the app, just run:
flask run

The app is set by default in dev mode, you can change it in .flaskenv