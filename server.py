from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from seleniumbase import Driver
import uvicorn
import time

app = FastAPI(title="Termux Undetected Browser Solver (FREE)")

class SolveRequest(BaseModel):
    type: str
    sitekey: str
    url: str

def solve_with_browser(page_url: str):
    print("[*] Sedang membuka browser penyamaran di background...")
    # Membuka browser rahasia (Undetected Mode) biar gak disangka bot oleh Cloudflare
    driver = Driver(uc=True, headless=True) 
    
    try:
        # Buka langsung link faucetnya bray
        driver.get(page_url)
        print("[*] Menunggu Turnstile memverifikasi koneksi (10-15 detik)...")
        time.sleep(12) # Memberi waktu browser menyelesaikan tantangan
        
        # Mengambil token hasil turnstile dari form h-captcha / cf-turnstile
        token = driver.execute_script("return (document.querySelector('[name=\"cf-turnstile-response\"]') || {}).value;")
        
        if not token:
            # Coba cari di elemen alternatif jika strukturnya beda
            token = driver.execute_script("return (document.querySelector('.cf-turnstile-response') || {}).value;")
            
        if token:
            return token
        else:
            raise Exception("Browser gagal mendapatkan token otomatis.")
            
    except Exception as e:
        raise Exception(f"Gagal saat proses browser: {str(e)}")
    finally:
        driver.quit()

@app.post("/solve")
async def solve(payload: SolveRequest):
    if payload.type != "turnstile":
        raise HTTPException(status_code=400, detail="Hanya mendukung type turnstile bray!")
        
    print(f"[+] Memproses bypass via Browser Termux untuk: {payload.url}")
    
    try:
        token = solve_with_browser(payload.url)
        print(f"[✓] Token Turnstile SUKSES Didapatkan!")
        return {"token": token}
    except Exception as e:
        print(f"[x] Gagal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Tetap di port 8877 biar sinkron otomatis sama faucet.js
    uvicorn.run(app, host="127.0.0.1", port=8877)
