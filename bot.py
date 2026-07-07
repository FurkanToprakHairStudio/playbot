import asyncio
import sys
import uuid
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 100  # Gönderilecek net bot sayısı
BEKLEME_SURESI = 90    # Sitede kalma süresi (90 saniye)
# ---------------

async def run_bot(playwright, index):
    browser = None
    try:
        browser = await playwright.chromium.launch(headless=True)
        
        context = await browser.new_context(
            user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Bot-{index}"
        )
        
        page = await context.new_page()
        await page.goto(HEDEF_SITE)
        
        # Python'da benzersiz UUID üretiyoruz
        generated_id = str(uuid.uuid4())
        
        # JavaScript tarafına değişkeni Playwright argümanı olarak güvenli bir şekilde paslıyoruz
        await page.evaluate("""(uid) => {
            localStorage.setItem('supabase.auth.token', JSON.stringify({ fake_user: uid }));
            localStorage.setItem('sb-uuid', uid);
        }""", generated_id)
        
        # Ağ bağlantılarının ve Supabase Realtime WebSocket akışının tamamen oturmasını bekle
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Başarıyla bağlandı! Supabase izole kimliği aktif.")
        
        # Sitede belirtilen süre boyunca kalıp sayacı şişiriyoruz
        await asyncio.sleep(BEKLEME_SURESI)
        
    except Exception as e:
        print(f"[Bot #{index}] Hata oluştu: {e}")
    finally:
        if browser:
            await browser.close()

async def main():
    print(f"[*] {HEDEF_SITE} adresine PROXYSIZ, %100 BAŞARILI {BAGLANTI_SAYISI} adet izole bot gönderiliyor...")
    
    async with async_playwright() as playwright:
        tasks = []
        for i in range(1, BAGLANTI_SAYISI + 1):
            tasks.append(run_bot(playwright, i))
            # Sunucuyu anlık yormamak için kısa aralıklarla sekmeleri sıraya koy
            await asyncio.sleep(0.15)  
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
