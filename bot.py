import asyncio
import sys
import uuid
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 100  # Görmek istediğin o net 100 sayısı!
BEKLEME_SURESI = 600   # Sitede kalma süresi (10 Dakika)
# ---------------

async def run_bot(playwright, index, browser):
    try:
        # En önemli kısım: Her bota tamamen sıfır, izole bir çerez ve hafıza odası açıyoruz
        context = await browser.new_context(
            user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Bot-{index}"
        )
        
        # Her odaya benzersiz bir Supabase kimliği (UUID) enjekte ediyoruz
        fake_uuid = str(uuid.uuid4())
        
        # Site açılmadan önce tarayıcının hafızasına bu kimlikleri kazıyoruz (Supabase IP'yi geçip buna bakacak)
        await context.add_init_script(f"""
            localStorage.setItem('supabase.auth.token', JSON.stringify({{ fake_user: '{fake_uuid}' }}));
            localStorage.setItem('sb-uuid', '{fake_uuid}');
        """)
        
        page = await context.new_page()
        
        # Sayfaya git ve WebSocket bağlantısının oturmasını bekle
        await page.goto(HEDEF_SITE)
        await page.wait_for_load_state("networkidle")
        
        print(f"[Bot #{index}] İçeride! Benzersiz Kimlik: {fake_uuid[:8]}")
        
        # Belirtilen süre boyunca bağlantıyı koparmadan odada kal
        await asyncio.sleep(BEKLEME_SURESI)
        
    except Exception as e:
        print(f"[Bot #{index}] Hata: {e}")

async def main():
    print(f"[*] PROXYSIZ %100 ÇÖZÜM: {HEDEF_SITE} adresine {BAGLANTI_SAYISI} adet izole bot enjekte ediliyor...")
    
    async with async_playwright() as playwright:
        # RAM'i korumak için tek bir ana tarayıcı motoru açıyoruz
        browser = await playwright.chromium.launch(headless=True)
        
        tasks = []
        for i in range(1, BAGLANTI_SAYISI + 1):
            # Ana motorun altında 100 tane izole oda tetikliyoruz
            tasks.append(run_bot(playwright, i, browser))
            # Sunucuyu anlık kilitlememek için milisaniyelik aralarla odaları aç
            await asyncio.sleep(0.1)  
            
        await asyncio.gather(*tasks)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
