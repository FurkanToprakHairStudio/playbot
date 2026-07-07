import asyncio
import sys
import aiohttp
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 150  # Her bir Actions çalışmasında hedeflenen maksimum bot sayısı
BEKLEME_SURESI = 500   # Sitede kalma süresi (2 dakika yaptık ki sen diğer workflowları başlatırken eskiler düşmesin)
# ---------------

async def fetch_proxies():
    """İnternetteki en büyük 6 ücretsiz havuzdan binlerce güncel proxy toplar"""
    urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=8000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://api.openproxylist.xyz/http.txt"
    ]
    proxies = set()
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url, timeout=6) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        for line in text.split("\n"):
                            line = line.strip()
                            if line and ":" in line and not line.startswith("#"):
                                proxies.add(line)
            except Exception:
                continue
    return list(proxies)

async def test_proxy(session, proxy_addr):
    """Proxy'yi hızlıca test eder, sağlamsa geri döndürür"""
    try:
        async with session.get("http://www.google.com", proxy=f"http://{proxy_addr}", timeout=3.5) as resp:
            if resp.status == 200:
                return proxy_addr
    except Exception:
        pass
    return None

async def run_bot(playwright, index, proxy):
    browser = None
    try:
        browser = await playwright.chromium.launch(
            headless=True,
            proxy={"server": f"http://{proxy}"}
        )
        context = await browser.new_context(
            user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Bot-Dev-{index}"
        )
        page = await context.new_page()
        page.set_default_timeout(25000)
        
        await page.goto(HEDEF_SITE)
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Giriş Başarılı! IP: {proxy}")
        
        await asyncio.sleep(BEKLEME_SURESI)
    except Exception:
        pass
    finally:
        if browser:
            await browser.close()

async def main():
    print(f"[*] {HEDEF_SITE} için devasa havuz taranıyor...")
    raw_proxies = await fetch_proxies()
    print(f"[+] Toplam {len(raw_proxies)} adet potansiyel proxy toplandı. Agresif canlılık testi başlıyor...")
    
    # Sınırı kaldırdık: İlk 1500 proxy'yi aynı anda jet hızıyla tarıyoruz!
    valid_proxies = []
    async with aiohttp.ClientSession() as session:
        tasks = [test_proxy(session, p) for p in raw_proxies[:1500]]
        results = await asyncio.gather(*tasks)
        valid_proxies = [p for p in results if p is not None]
        
    print(f"[+] Testi geçen CANLI proxy sayısı: {len(valid_proxies)}. Saldırı ordusu kuruluyor...")
    
    if not valid_proxies:
        print("[-] Şansımıza canlı proxy bulunamadı, tekrar tetikleyin.")
        return

    async with async_playwright() as playwright:
        tasks = []
        loop_limit = min(BAGLANTI_SAYISI, len(valid_proxies))
        for i in range(loop_limit):
            tasks.append(run_bot(playwright, i+1, valid_proxies[i]))
            await asyncio.sleep(0.15)
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
