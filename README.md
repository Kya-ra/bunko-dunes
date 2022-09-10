# Bunko :)

DU Gamers Discord service bot.

Was going to set up ci-cd for the server, but for robustness and security, just clone the repository and set up a service to keep it live with systemctl. Use the example .service file if you'd like.

Recently moved to Google Sheets API instead of using SheetDB, for the higher request limits.

The "sheets_api.py" file is the interface for that. Uses a Google Cloud Service Account, 
which wasn't *easy* by any means but it did work much better than OAuth. Would rec.