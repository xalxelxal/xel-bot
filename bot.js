const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const bot = new TelegramBot(process.env.TOKEN, { polling: true });
console.log("xel bot nyala...");

const APIS = [
  "https://apii.bagusee.my.id/api/cekkuota?msisdn=",
  "https://api.cekkuota.my.id/api/cekkuota?msisdn=",
  "https://sidompul.vanjava.my.id/api/cekkuota?msisdn="
];

async function cekKuota(nomor) {
  let num = nomor.replace(/\D/g,'');
  if(num.startsWith('0')) num = '62'+num.slice(1);
  for(let base of APIS){
    try{
      const res = await axios.get(base+num, {timeout: 15000});
      if(res.data) return res.data;
    }catch(e){ console.log("API gagal:", base, e.message); }
  }
  throw new Error("Semua API mati");
}

bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, "Halo Sal! Bot xel udah nyala ✅\nKetik: /cek 0877xxxx");
});

bot.onText(/\/cek (.+)/, async (msg, match) => {
  const chatId = msg.chat.id;
  const nomor = match[1];
  bot.sendMessage(chatId, `⏳ xel lagi ngecek ${nomor}...`);
  try{
    const data = await cekKuota(nomor);
    let hasil = `✅ Hasil cek ${nomor}\n\n`;
    if(typeof data === 'object') hasil += JSON.stringify(data, null, 2).substring(0, 3500);
    else hasil += data;
    bot.sendMessage(chatId, hasil);
  }catch(err){
    bot.sendMessage(chatId, `❌ Gagal cek ${nomor}\nError: ${err.message}\nCoba lagi 1 menit.`);
  }
});
