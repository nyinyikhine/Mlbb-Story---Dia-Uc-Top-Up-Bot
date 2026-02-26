import os
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# --- Configurations (ဤနေရာတွင် သင်၏ အချက်အလက်များ အစားထိုးပါ) ---
PAGE_ACCESS_TOKEN = "EAAcjCvOQ2XIBQ12TvWGnZCdLO28vpq9tmt4YuCDaZBuOcTEXd4XL31ycKTLReHprKMatvOrG5v3o0mcOhal3bryVJM495cIozkxBpsZBWHrK5JGSX7z7Pp4WRL08vVPhFZCbHsEJT3IyledmI42GugCEvRcwzydG2ZBsfOAfLhSXzlqc5oxjxoeCVlk7AkjfrCD3j" # Facebook မှရသော Token
VERIFY_TOKEN = "my_mlbb_bot_123"             # Facebook Webhook တွင် ထည့်ရမည့်စာသား
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbxS3JzeTCCGcockMspTObcZG2SvI-3s9BFVxwMA5H0n4DuK0N8cotNHyBshb6XHabNdQQ/exec" # Google App Script မှရသော URL

# စိန်စျေးနှုန်းများ (အလိုအလျောက် စာပြန်ရန်)
DIAMOND_PRICES = {
    "86": "3,500 Ks",
    "172": "6,800 Ks",
    "257": "10,500 Ks",
    "706": "28,000 Ks"
}

# --- Helper Functions ---
def send_message(recipient_id, message_text):
    """Messenger ဆီ စာပြန်ပို့ပေးသည့် Function"""
    params = {"access_token": PAGE_ACCESS_TOKEN}
    data = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, json=data)

def send_to_google_sheet(user_id, player_info):
    """Google Sheet ထံ အချက်အလက်လှမ်းပို့ခြင်း"""
    payload = {"user_id": user_id, "player_info": player_info}
    try:
        requests.post(GOOGLE_SHEET_URL, json=payload)
    except Exception as e:
        print(f"Error sending to Google Sheets: {e}")

# --- Routes ---

@app.route('/', methods=['GET'])
def verify():
    """Facebook Webhook နှင့် ချိတ်ဆက်မှု စစ်ဆေးခြင်း"""
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Bot is Running!", 200

@app.route('/', methods=['POST'])
def webhook():
    """Customer ဆီက စာဝင်လာလျှင် လုပ်ဆောင်မည့်အပိုင်း"""
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"].get("text", "").strip()

                    # ၁. စျေးနှုန်းမေးမြန်းခြင်း
                    if user_text.lower() in ["hi", "hello", "price", "စျေးနှုန်း"]:
                        price_msg = "💎 MLBB Diamond စျေးနှုန်းများ 💎\n\n"
                        for amt, price in DIAMOND_PRICES.items():
                            price_msg += f"• {amt} Diamonds - {price}\n"
                        price_msg += "\nဝယ်ယူရန် Player ID နဲ့ Server ID (ဥပမာ - 12345678 1234) ကို ရိုက်ပို့ပေးပါ။"
                        send_message(sender_id, price_msg)

                    # ၂. ID လက်ခံရရှိခြင်း (ဂဏန်းများပါပြီး ၅ လုံးထက်ကျော်လျှင် ID ဟု သတ်မှတ်သည်)
                    elif any(char.isdigit() for char in user_text) and len(user_text) > 5:
                        send_to_google_sheet(sender_id, user_text)
                        response = f"ID: {user_text} ကို လက်ခံရရှိပါသည်။ Google Sheet ထဲတွင် အော်ဒါတင်လိုက်ပါပြီ။\n\nကျေးဇူးပြု၍ ငွေလွှဲ Screenshot ပို့ပေးပါ။ Admin မှ စစ်ဆေးပြီး ထည့်ပေးပါမည်။"
                        send_message(sender_id, response)
                    
                    # ၃. အခြားစာများအတွက်
                    else:
                        send_message(sender_id, "မင်္ဂလာပါ၊ စိန်စျေးနှုန်းကြည့်ရန် 'Price' ဟု ပို့ပေးပါ။")
                        
    return "ok", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
