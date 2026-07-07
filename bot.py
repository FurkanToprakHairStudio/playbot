import asyncio
import sys
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 20  # Supabase sayaçta görünecek bot sayısı
BEKLEME_SURESI = 45   # Sitede kaç saniye açık kalacaklar (Supabase sinyali için ideal süre)
# ---------------

async def run_bot(playwright, index):
    try:
        # Arka planda gizli bir tarayıcı (headless Chrome) başlatıyoruz
        browser = await playwright.chromium.launch(headless=True)
        
        # Gerçek bir insan tarayıcısı süsü vermek için User-Agent tanımlıyoruz
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        print(f"[Bot #{index}] Tarayıcı sekmesi açıldı. Siteye gidiliyor...")
        
        # Siteye giriş yap
        await page.goto(HEDEF_SITE)
        
        # JavaScript'lerin ve Supabase Realtime bağlantısının tamamen oturmasını bekle
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Supabase Realtime bağlantısı kuruldu! Sayaç tetiklendi.")
        
        # Belirttiğimiz süre boyunca sekmeyi kapatma, sitede asılı kalsınlar
        await asyncio.sleep(BEKLEME_SURESI)
        
        print(f"[Bot #{index}] Süre doldu, sekme kapatılıyor.")
        await browser.close()
        
    except Exception as e:
        print(f"[Bot #{index}] Hata oluştu: {e}")

async def main():
    print(f"Hedef siteye ({HEDEF_SITE}) {BAGLANTI_SAYISI} adet CANLI TARAYICI botu gönderiliyor...")
    
    async with async_playwright() as playwright:
        tasks = []
        for i in range(1, BAGLANTI_SAYISI + 1):
            tasks.append(run_bot(playwright, i))
            # GitHub sunucusunu anlık kilitlememek için yarım saniye arayla sekmeleri aç
            await asyncio.sleep(0.5)  
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
