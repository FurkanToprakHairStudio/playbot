import asyncio
import sys
import aiohttp

# --- AYARLAR ---
# Bot yollamak istediğin web sitesinin adresi (Test için kendi siteni veya herhangi bir adresi yazabilirsin)
HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/" 
BAGLANTI_SAYISI = 20  # Gönderilecek toplam bot/istek sayısı
# ---------------

async def send_request(session, index):
    try:
        # Web sitesine asenkron (eşzamanlı) olarak ziyaret isteği gönderiyoruz
        async with session.get(HEDEF_SITE) as response:
            status = response.status
            # Eğer site IP gösteren bir yerse gelen veriyi okuyalım
            text = await response.text()
            print(f"[Bot #{index}] Siteye giriş yaptı! Durum Kodu: {status} | Sunucu Yanıtı: {text.strip()}")
    except Exception as e:
        print(f"[Bot #{index}] Siteye bağlanırken hata oluştu: {e}")

async def main():
    print(f"Hedef siteye ({HEDEF_SITE}) GitHub sunucusu üzerinden {BAGLANTI_SAYISI} adet bot isteği başlatılıyor...")
    
    # Tüm botların tek bir oturum üzerinden hızlıca istek atmasını sağlıyoruz
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, BAGLANTI_SAYISI + 1):
            tasks.append(asyncio.create_task(send_request(session, i)))
            await asyncio.sleep(0.1) # İstekleri milisaniyelik aralarla yayıyoruz
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())
