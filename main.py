import threading, re, time, html, os, urllib3, requests, asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- BAGIAN API DARI FILE.PY KAMU ---
urllib3.disable_warnings()
app = Flask(__name__)

def clean_phone_number(number):
    number = re.sub(r'[^0-9]', '', number)
    if number.startswith('62'): number = '0' + number[2:]
    return number

def parse_packages_from_html(html_content):
    clean_res = re.sub(r'<(script|style)[^>]*?>.*?</\1>', '', html_content, flags=re.I | re.DOTALL)
    clean_text = re.sub(r'<[^>]+>', '', clean_res)
    clean_text = html.unescape(clean_text)
    sn_match = re.search(r'SN/Ref\s*[:=]?\s*(.*?)(?=rusmanaid|Telp\.|Nominal|Harga|Tanggal|Print|Komplain|Testimonial|$)', clean_text, re.I | re.DOTALL)
    if not sn_match: return []
    raw_result = sn_match.group(1).strip()
    raw_result = re.sub(r'pesan\s*[:\=].*$', '', raw_result, flags=re.I | re.DOTALL)
    raw_result = re.sub(r'[\r\n\t]+', ' ', raw_result).strip()
    packages_raw = [p.strip(" -,;") for p in raw_result.split('|||') if p.strip()]
    return list(dict.fromkeys(packages_raw))

@app.route('/')
def home(): return 'xel API + Bot jalan!'
@app.route('/cek_kuota', methods=['POST'])
def cek_kuota():
    # ... (copy paste isi fungsi cek_kuota dari file.py kamu yang asli) ...
    # biar pendek, pake yang kamu kirim tadi persis
    try:
        no_raw = request.form.get('no',''); id_op = request.form.get('id','')
        if not no_raw or not id_op: return jsonify({'status':'error'}),400
        no = clean_phone_number(no_raw); ids, prd, op = id_op.split(',')
        session = requests.Session()
        ua = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36'
        resp_get = session.get('https://orderkuota.com/', headers={'User-Agent':ua}, verify=False, timeout=30)
        phpsessid = session.cookies.get('PHPSESSID',''); csrf_cookie = session.cookies.get('csrf_cookie','')
        if not csrf_cookie:
            m = re.search(r'name="csrf_token"\s+value="([^"]+)"', resp_get.text)
            if m: csrf_cookie = m.group(1)
            else: return jsonify({'status':'fail','message':'Gagal CSRF'}),500
        headers = {'User-Agent':ua, 'Cookie': f'PHPSESSID={phpsessid}; user_id=MzAwMDMwMQ%3D%3D; user_key=8c96570b661c2e7ed3a4d46fbc432723; csrf_cookie={csrf_cookie}', 'Content-Type':'application/x-www-form-urlencoded'}
        payload = {'csrf_token':csrf_cookie,'nomor_hp':'083879017166','pembayaran':'balance','produk':prd,'operator':op,'voucher':ids,'id_plgn':no,'json_format':1}
        req1 = session.post("https://orderkuota.com/cetak_voucher", data=payload, headers=headers, verify=False, timeout=60)
        res1 = req1.text
        if "Sedang rekap dan pembukuan" in res1: return jsonify({'status':'fail','message':'Lagi rekap 23.40-00.10'})
        if "errors" in res1.lower(): return jsonify({'status':'fail','message': req1.json()['errors'][0]})
        id_trx = req1.json().get('id','')
        time.sleep(5); session.get(f"https://orderkuota.com/cek-status/trx/{id_trx}", headers=headers, verify=False)
        time.sleep(7)
        req_view = session.get(f"https://orderkuota.com/akun/riwayat-transaksi/view/{id_trx}", headers=headers, verify=False)
        res_view = req_view.text
        if "SN/Ref" not in res_view: return jsonify({'status':'fail','message':'SN/Ref tidak ketemu'})
        packages = parse_packages_from_html(res_view)
        return jsonify({'status':'success','data':{'nomor':no,'packages':packages}})
    except Exception as e: return jsonify({'status':'error','message':str(e)}),500

# --- BAGIAN BOT TELEGRAM ---
TOKEN = os.getenv("TOKEN")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot xel aktif ✅\nKetik: /cek 087777133929")

async def cek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("Pakai: /cek 0877xxxx")
    nomor = clean_phone_number(context.args[0])
    await update.message.reply_text(f"⏳ xel ngecek {nomor} via orderkuota...")
    try:
        r = requests.post(f"http://127.0.0.1:5000/cek_kuota", data={'no':nomor,'id':'0,XL_DATA,0'}, timeout=90)
        j = r.json()
        if j.get('status')=='success':
            txt = f"✅ {nomor}\n\n" + "\n".join(j['data']['packages'])
            await update.message.reply_text(txt[:4000])
        else:
            await update.message.reply_text(f"❌ {j.get('message')}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def run_bot():
    app_bot = Application.builder().token(TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("cek", cek))
    app_bot.run_polling()

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.getenv("PORT",5000))), daemon=True).start()
    run_bot()
