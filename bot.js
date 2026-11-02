const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const bot = new TelegramBot(process.env.TOKEN, { polling: true });
console.log("Bot xel dmpl jalan...");

// List API yang masih hidup per hari ini
const APIS = [
  (n) => `https://sidompul.tembakaxis.my.id/cekkuota?nomor=${n}`,
  (n) => `https://api.cekkuota.my.id/cek?msisdn=${n}`,
  (n) => `https://api.my-xl.com/kuota?msisdn=${n}`,
  (n) => `https://apii.bagusee.my.id/api/cekkuota?msisdn=${n}`, // fallback lama
];

async function cekXL(nomor){
  let num = nomor.replace(/\D/g,'');
  if(num.startsWith('0')) num = '62'+num.slice(1);
  if(num.startsWith('62')) {} else num = '62'+num;
  
  for(let makeUrl of APIS){
    let url = makeUrl(num);
    try{
      console.log("Coba:", url);
      let res = await axios.get(url, {timeout: 12000, headers:{'User-Agent':'Mozilla/5.0'}});
      let data = res.data;
      // kalau data ada kuota nya, langsung balikin
      if(data && (data.data || data.kuota || data.result || data.success !== false)){
        return data;
      }
    }catch(e){
      console.log("Gagal", url, e.message);
    }
  }
  throw new Error("Semua API lagi down, coba lagi 5 menit");
}

bot.onText(/\/start/, (m)=>{
  bot.sendMessage(m.chat.id, "Bot xel dmpl aktif ✅\nCara: /cek 0877xxxxxx");
});

bot.onText(/\/cek (.+)/, async (msg, match)=>{
  let nomor = match[1].trim();
  let chatId = msg.chat.id;
  await bot.sendMessage(chatId, `⏳ xel lagi ngecek ${nomor}...`);
  try{
    let hasil = await cekXL(nomor);
    let txt = `✅ Hasil ${nomor}\n\n`;
    txt += "```\n" + JSON.stringify(hasil, null, 2).slice(0,3800) + "\n```";
    bot.sendMessage(chatId, txt, {parse_mode:"Markdown"});
  }catch(err){
    bot.sendMessage(chatId, `❌ Gagal cek ${nomor}\n${err.message}\n\nAPI sidompul emang sering maintenance sore, coba lagi nanti.`);
  }
});
