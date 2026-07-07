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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Bot-" + str(index)
        )
        
        page = await context.new_page()
        await page.goto(HEDEF_SITE)
        
        # Format hatasını engellemek için JavaScript stringini dışarıda birleştiriyoruz
        fake_uuid = str(uuid.uuid4())
        js_code = """
            localStorage.setItem('supabase.auth.token', '{"fake_user": "' + fake_uuid + '"}');
            localStorage.setItem('sb-uuid', '""" + fake_uuid + """');
        """
        
        await page.evaluate(js_code)
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Başarıyla bağlandı! Supabase izole kimliği: {fake_uuid[:8]}...")
        
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
            await asyncio.sleep(0.15)  
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
