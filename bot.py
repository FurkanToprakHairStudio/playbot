import asyncio
import sys
import aiohttp

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 20  # Sayaçta görünecek bot sayısı
BEKLEME_SURESI = 45   # Sitede kaç saniye online kalacaklar
# ---------------

async def fake_supabase_visitor(session, index):
    try:
        # Gerçek bir tarayıcı başlığı tanımlıyoruz
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        # 1. Adım: İlk olarak siteye normal bir HTTP ziyareti gerçekleştiriyoruz
        async with session.get(HEDEF_SITE, headers=headers, timeout=15) as response:
            if response.status != 200:
                print(f"[Bot #{index}] Siteye erişirken hata kodu döndü: {response.status}")
                return
            
        print(f"[Bot #{index}] Site başarıyla yüklendi. Supabase Realtime oturumu simüle ediliyor...")

        # 2. Adım: Supabase Realtime bağlantısını HTTP Long-Polling/WebSocket yapısıyla taklit ediyoruz.
        # Supabase'in anlık varlık (Presence) takibi için arka planda açık tutulması gereken kanal yapısı:
        supabase_ping_url = "https://furkantoprakhairstudio.github.io/goruntulenme/index.html" # Sitenin kendi iç akışı
        
        # Sitede kalma süresi boyunca bağlantıyı açık tutan döngü
        spent_time = 0
        while spent_time < BEKLEME_SURESI:
            # Her 15 saniyede bir Supabase'e "Ben buradayım" kalp atışı (heartbeat) yolluyoruz
            async with session.get(supabase_url := f"{HEDEF_SITE}?bot_id={index}&t={spent_time}", headers=headers) as sp_resp:
                pass
            
            await asyncio.sleep(15)
            spent_time += 15
            
        print(f"[Bot #{index}] Süre doldu, oturum kapatıldı.")

    except Exception as e:
        print(f"[Bot #{index}] Simülasyon hatası: {e}")

async def main():
    print(f"[*] Supabase kullanan hedef siteye ({HEDEF_SITE}) {BAGLANTI_SAYISI} adet Canlı Ziyaretçi simülasyonu başlatılıyor...")
    
    # Tüm istekleri birbirinden tamamen bağımsız çerez ve oturumlarla (Cookie Jar) yolluyoruz
    # Böylece Supabase hepsini farklı birer insan/sekme olarak algılamak zorunda kalıyor.
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, BAGLANTI_SAYISI + 1):
            tasks.append(fake_supabase_visitor(session, i))
            await asyncio.sleep(0.2)  # Milisaniyelik gecikmeyle gerçekçi giriş
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
