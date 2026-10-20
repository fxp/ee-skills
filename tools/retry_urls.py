"""Re-probe the URLs that failed in urlcheck.txt with curl (longer timeout, browser UA). Usage: retry_urls.py urlcheck.txt"""
import subprocess, sys, concurrent.futures as cf
urls = [l.split()[2] for l in open(sys.argv[1]) if l.startswith("URL")]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def probe(u):
    r = subprocess.run(["curl", "-sS", "-L", "-o", "/dev/null", "-m", "45", "-A", UA, "-w", "%{http_code}", u], capture_output=True, text=True)
    return u, (r.stdout.strip() or r.stderr.strip()[:60])
with cf.ThreadPoolExecutor(8) as ex:
    for u, st in ex.map(probe, urls):
        print(st, u)
