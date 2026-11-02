const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

const TOKEN = process.env.TOKEN; // isi dari Environment di wokku
if (!TOKEN) throw new Error("TOKEN belum di-set!");

const bot = new TelegramBot(TOKEN, { polling: true });
console.log("🤖 Bot xel jalan...");

bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, 
`👋 Halo! Aku *xel* - Bot Cek Kuota XL/Axis

Cara pakai:
/cek 0878xxxxxx
/cek 62878xxxxxx

Bot bakal ngasih sisa kuota, masa aktif & paket yang nempel.

Made by Sal`,
  {parse_mode: "Markdown"}
  );
});

bot.onText(/\/cek (.+)/, async (msg, match) => {
  const chatId = msg.chat.id;
  let nomor = match[1].replace(/\D/g, ""); // hanya angka

  if (nomor.startsWith("0")) nomor = "62" + nomor.slice(1);
  if (!nomor.startsWith("62")) nomor = "62" + nomor;

  await bot.sendMessage(chatId, `⏳ *xel* lagi ngecek ${nomor}...`, {parse_mode: "Markdown"});

  try {
    // GANTI API INI kalau error, pake API sidompul yang kamu punya
    const url = `https://apii.bagusee.my.id/api/cekxl?nomor=${nomor}`;
    const res = await axios.get(url, {timeout: 15000});

    const data = res.data;
    let text = `✅ *Hasil Cek XL - xel*\n`;
    text += `📱 Nomor: \`${nomor}\`\n`;
    text += `─────────────────\n`;
    text += `\`\`\`${JSON.stringify(data, null, 2)}\`\`\``;

    // Kalau API balikin format rapi
    if (data && data.data) {
       text = `✅ *Hasil Cek XL - xel*\n📱 \`${nomor}\`\n\n${data.data}`;
    }

    bot.sendMessage(chatId, text, {parse_mode: "Markdown"});
  } catch (e) {
    bot.sendMessage(chatId, `❌ Gagal cek ${nomor}\nCoba lagi 1 menit lagi.\n\nError: ${e.message}\n\nAPI mungkin lagi maintenance, coba ganti API di file bot.js`);
  }
});
