from flask import Flask, request, jsonify
import requests
from playwright.sync_api import sync_playwright
from telegram import Bot

# Telegram Bot Token and Chat ID (replace with your values)
BOT_TOKEN = "7424414158:AAEcGXR_RP5orU7Cz_Aw1lmM9Awp6n1zQq8"
CHAT_ID = "6233962537"

# Flask app
app = Flask(__name__)


@app.route('/tradingview-alert', methods=['POST'])
def tradingview_alert():
    """Handle TradingView alerts."""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    asset = data.get("ticker", "Unknown Asset")
    volume = data.get("volume", "Unknown Volume")
    alert_message = f"🚨 Alert for {asset}!\n📊 Volume: {volume}\n"

    # Capture TradingView chart screenshot
    try:
        screenshot_path = capture_chart_screenshot(asset)
        send_telegram_alert(alert_message, screenshot_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "Alert sent successfully!"}), 200


def capture_chart_screenshot(asset):
    """Capture a screenshot of the TradingView chart."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = f"https://www.tradingview.com/symbols/{asset}/"
        page.goto(url)
        page.wait_for_timeout(5000)  # Wait for the page to load
        screenshot_path = f"{asset}_chart.png"
        page.screenshot(path=screenshot_path, full_page=True)
        browser.close()
    return screenshot_path


def send_telegram_alert(message, screenshot_path):
    """Send an alert message with a chart screenshot to Telegram."""
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)
    with open(screenshot_path, "rb") as photo:
        bot.send_photo(chat_id=CHAT_ID, photo=photo)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
