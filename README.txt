TradingBot for Render.com (Dark Theme) - quick deploy

What's inside:
- bot.py          -> The Telegram bot code (uses BOT_TOKEN from environment)
- requirements.txt -> Python dependencies
- Procfile        -> Render start command
- README.txt      -> This file

How to deploy on Render (very short):
1) Create a GitHub repository and push these files into it (or upload via Render UI).
2) Sign in to https://render.com and create a new Web Service.
   - Connect your GitHub repo (select the repository with these files).
   - Build Command: (leave empty) or use: pip install -r requirements.txt
   - Start Command: (Render will use Procfile) OR set to: python bot.py
3) After the service is created, go to Service -> Environment -> Environment Variables
   - Add a variable named: BOT_TOKEN
   - Value: your bot token from @BotFather (e.g. 123456789:AA...).
4) Deploy / Redeploy. The service will start and keep your bot running 24/7.

Notes / Tips:
- Use a Worker or Web service on Render; this Procfile uses "web" type. For background-only, you can create a "Private Service" or use a worker on paid plan.
- To check logs on Render, open the service and view "Logs" tab.
- If you change bot.py, push new commits to GitHub; Render will redeploy (if enabled).

Security:
- Do NOT hardcode BOT_TOKEN into the code. Use Render environment variables.
- Keep your token secret. If the token leaks, regenerate it with @BotFather.
