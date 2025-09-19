import discord
from threading import Thread
from playwright.sync_api import sync_playwright
import requests
import time

# ANSI color codes for console
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Discord bot token
BOT_TOKEN = "MTQxODMyODc3OTI1MTUxNTUxNA.GoLRco.bxudSxqkBy5k_0Cg3qxrNtuGuZc2GsCoRJiL1M"  # Replace with your bot token

# Discord webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1417997472197902427/WtGyA1pBdeLw1ILz_VNm1Nm0O2n35Gwdh_fELws26EiIJOsDFPcJFoCrtjKWbIF2VD-g"

# Keep track of monitored tokens to avoid duplicate alerts
monitored_tokens = set()

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

def send_discord_alert(contract):
    """Send a clean alert to Discord via webhook."""
    token_url = f"https://pump.fun/coin/{contract}"
    data = {
        "embeds": [{
            "title": "🚀 Pump.Fun Live Token Alert",
            "url": token_url,
            "description": f"Token **`{contract}`** is now **LIVE** on Pump.Fun!\n\n🔗 [View Token]({token_url})",
            "color": 0x00ff00,
            "footer": {"text": "Pump.fun Live Tracker Bot"}
        }]
    }
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print(f"{RED}Failed to send webhook: {response.status_code} - {response.text}{RESET}")

def check_token_live(contract_address):
    """Check if token is live on pump.fun."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        token_url = f"https://pump.fun/coin/{contract_address}"
        page.goto(token_url)
        page.wait_for_timeout(5000)
        live_badge = page.query_selector('[data-testid="live-badge"]')
        browser.close()
        return bool(live_badge)

def process_contract(contract):
    """Check live status and send alert if live."""
    if contract in monitored_tokens:
        return
    print(f"{GREEN}Captured contract: {contract}{RESET}")
    try:
        is_live = check_token_live(contract)
        status = f"{GREEN}LIVE{RESET}" if is_live else f"{RED}NOT LIVE{RESET}"
        print(f"Token {contract}: {status}")
        if is_live:
            send_discord_alert(contract)
        monitored_tokens.add(contract)
    except Exception as e:
        print(f"{RED}Error checking token: {e}{RESET}")

@bot.event
async def on_ready():
    print(f"{GREEN}Bot logged in as {bot.user}{RESET}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.strip()
    # Capture contracts: 44 chars ending with 'pump'
    if len(content) == 44 and content.lower().endswith("pump"):
        # Run Playwright check in a separate thread to avoid blocking
        Thread(target=process_contract, args=(content,)).start()

# Run the bot
bot.run(BOT_TOKEN)
