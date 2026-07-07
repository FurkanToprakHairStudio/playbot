import asyncio
import sys
import aiohttp
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 999  # Arttırılan hedef canlı ziyaretçi sayısı
BEKLEME_SURESI = 900    # Sitede kalma süresi (90 saniyeye çıkardık ki sayaç iyice otursun)
# ---------------

async def get_all_free_proxies():
    """Çoklu kaynaklardan binlerce güncel proxy adresi toplar"""
    proxies = set()
    urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
    ]
    
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url, timeout=8) as response:
                    if response.status == 200:
                        text = await response.text()
                        for line in text.split("\n"):
                            line = line.strip()
                            if line and ":" in line:
                                proxies.add(line)
            except Exception:
                continue
                
    proxy_list = list(proxies)
    print(f"[+] Toplam {len(proxy_list)} adet benzersiz proxy havuzu oluşturuldu.")
    return proxy_list

async def run_bot(playwright, index, proxy_address):
    browser = None
    try:
        launch_args = {}
        if proxy_address:
            launch_args["proxy"] = {"server": f"http://{proxy_address}"}
        
        browser = await playwright.chromium.launch(headless=True, **launch_args)
        
        # Her bota tamamen izole tarayıcı profili tanımlıyoruz
        context = await browser.new_context(
            user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Bot-{index}"
        )
        
        page = await context.new_page()
        page.set_default_timeout(35000) # Yanıt vermeyen proxyler zaman kaybettirmesin
        
        await page.goto(HEDEF_SITE)
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Başarılı! Farklı IP ile Supabase odasına giriş yapıldı.")
        
        await asyncio.sleep(BEKLEME_SURESI)
        
    except Exception:
        # Log kalabalığı yapmaması için başarısız proxyleri sessizce geçiyoruz
        pass
    finally:
        if browser:
            await browser.close()

async def main():
    print(f"[*] Hedef siteye ({HEDEF_SITE}) büyük operasyon başlatılıyor: {BAGLANTI_SAYISI} Bot hedefi!")
    
    proxies = await get_all_free_proxies()
    if not proxies:
        print("[-] Proxy havuzu boş kaldı, işlem iptal edildi.")
        return
        
    async with async_playwright() as playwright:
        tasks = []
        for i in range(1, BAGLANTI_SAYISI + 1):
            # Havuzdan sırayla her bota farklı bir proxy paslıyoruz
            proxy = proxies[i % len(proxies)]
            tasks.append(run_bot(playwright, i, proxy))
            # GitHub Actions sunucusunu birden çökertmemek için her bot arasında çeyrek saniye bekle
            await asyncio.sleep(0.25)  
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
