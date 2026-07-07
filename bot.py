import asyncio
import sys
import uuid
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

# Buraya istediğin hedef sayıyı yazabilirsin (Örn: 100, 200, 500)
# GitHub sunucusunun kilitlenmemesi için 100-150 arası çok stabil çalışır.
BAGLANTI_SAYISI = 100  
BEKLEME_SURESI = 90    # Sitede kalacakları süre (saniye cinsinden)
# ---------------

async def run_bot(playwright, index):
    browser = None
    try:
        # Proxy OLMADAN, doğrudan ve çok hızlı şekilde tarayıcıyı açıyoruz
        browser = await playwright.chromium.launch(headless=True)
        
        # Her bir bota tamamen izole, sıfır bir çerez odası açıyoruz
        context = await browser.new_context(
            user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Bot-{index}"
        )
        
        page = await context.new_page()
        
        # Siteye hızlıca giriş yap
        await page.goto(HEDEF_SITE)
        
        # Supabase'i tamamen ikna edecek BENZERSİZ KULLANICI KİMLİĞİNİ (UUID) tarayıcı hafızasına ekiyoruz
        fake_uuid = str(uuid.uuid4())
        await page.evaluate(f"""
            localStorage.setItem('supabase.auth.token', '{"fake_user": "{fake_uuid}"}');
            localStorage.setItem('sb-uuid', '{fake_uuid}');
        """)
        
        # Sayfa bağlantısının ve WebSocket el sınırlarının tamamen oturmasını bekle
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Başarıyla bağlandı! Supabase izole kimliği: {fake_uuid[:8]}...")
        
        # Belirtilen süre boyunca odada kal ve sayacı yüksek tut
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
            # GitHub sunucusunu yormamak için çok kısa aralıklarla sekmeleri aç
            await asyncio.sleep(0.15)  
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
