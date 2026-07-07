import asyncio
import sys
import aiohttp
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 20  
BEKLEME_SURESI = 60   
# ---------------

async def get_free_proxies():
    """İnternetten güncel ücretsiz proxy listesini çeker"""
    try:
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    proxies = [line.strip() for line in text.split("\n") if line.strip()]
                    print(f"[+] {len(proxies)} adet güncel proxy adresi toplandı.")
                    return proxies
    except Exception as e:
        print(f"[-] Proxy listesi alınamadı: {e}")
    return []

async def run_bot(playwright, index, proxy_address=None):
    browser = None
    try:
        # Eğer proxy varsa tarayıcıya entegre ediyoruz
        launch_args = {}
        if proxy_address:
            launch_args["proxy"] = {"server": f"http://{proxy_address}"}
            print(f"[Bot #{index}] Proxy tanımlandı: {proxy_address}")
        
        browser = await playwright.chromium.launch(headless=True, **launch_args)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        # Proxy yavaş olabileceği için zaman aşımını 45 saniyeye çıkartıyoruz
        page.set_default_timeout(45000) 
        
        await page.goto(HEDEF_SITE)
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Farklı IP ile Supabase Realtime bağlantısı tetiklendi!")
        
        await asyncio.sleep(BEKLEME_SURESI)
        
    except Exception as e:
        print(f"[Bot #{index}] Bağlantı başarısız (Proxy kaynaklı olabilir): {e}")
    finally:
        if browser:
            await browser.close()

async def main():
    print(f"[*] Hedef siteye ({HEDEF_SITE}) Proxy destekli {BAGLANTI_SAYISI} adet bot gönderiliyor...")
    
    # Güncel IP listesini çek
    proxies = await get_free_proxies()
    
    async with async_playwright() as playwright:
        tasks = []
        for i in range(1, BAGLANTI_SAYISI + 1):
            # Her bota listeden farklı bir proxy atıyoruz
            proxy = proxies[i % len(proxies)] if proxies else None
            tasks.append(run_bot(playwright, i, proxy))
            await asyncio.sleep(0.5)  
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
