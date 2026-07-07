import asyncio
import sys
import aiohttp
from playwright.async_api import async_playwright

# --- AYARLAR ---
if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    HEDEF_SITE = sys.argv[1]
else:
    HEDEF_SITE = "https://furkantoprakhairstudio.github.io/goruntulenme/"

BAGLANTI_SAYISI = 50   # Çok fazla proxy'yi aynı anda yormamak için ilk aşamada 50 idealdir
BEKLEME_SURESI = 90    # Sitede kalma süresi
# ---------------

async def fetch_proxies():
    """Ücretsiz havuzlardan hızlıca proxy listesini çeker"""
    urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=8000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ]
    proxies = set()
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        for line in text.split("\n"):
                            line = line.strip()
                            if line and ":" in line:
                                proxies.add(line)
            except Exception:
                continue
    return list(proxies)

async def test_proxy(session, proxy_addr):
    """Proxy'nin gerçekten çalışıp çalışmadığını saniyeler içinde test eder"""
    try:
        # Google üzerinden hızlı bir ping testi yapıyoruz
        async with session.get("http://www.google.com", proxy=f"http://{proxy_addr}", timeout=4) as resp:
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
            user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Bot-{index}"
        )
        page = await context.new_page()
        page.set_default_timeout(25000) # Canlı proxy olduğu için çok bekletmeye gerek yok
        
        await page.goto(HEDEF_SITE)
        await page.wait_for_load_state("networkidle")
        print(f"[Bot #{index}] Başarılı! Sağlam IP ile Supabase odasına girildi: {proxy}")
        
        await asyncio.sleep(BEKLEME_SURESI)
    except Exception:
        pass
    finally:
        if browser:
            await browser.close()

async def main():
    print(f"[*] {HEDEF_SITE} için proxy listesi toplanıyor...")
    raw_proxies = await fetch_proxies()
    print(f"[+] Toplam {len(raw_proxies)} proxy adresi bulundu. Canlılık testi başlatılıyor...")
    
    # Hızlıca çalışan en sağlam proxy'leri ayıklıyoruz
    valid_proxies = []
    async with aiohttp.ClientSession() as session:
        tasks = [test_proxy(session, p) for p in raw_proxies[:300]] # İlk 300 proxy'yi test et
        results = await asyncio.gather(*tasks)
        valid_proxies = [p for p in results if p is not None]
        
    print(f"[+] Testi geçen SAĞLAM proxy sayısı: {len(valid_proxies)}. Operasyon başlıyor...")
    
    if not valid_proxies:
        print("[-] Şansımıza o saniye canlı proxy denk gelmedi, lütfen tekrar tetikleyin.")
        return

    async with async_playwright() as playwright:
        tasks = []
        # Testi geçen sağlam proxy sayısı kadar veya hedef bağlantı sayısı kadar bot oluştur
        loop_limit = min(BAGLANTI_SAYISI, len(valid_proxies))
        for i in range(loop_limit):
            tasks.append(run_bot(playwright, i+1, valid_proxies[i]))
            await asyncio.sleep(0.2)
            
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
