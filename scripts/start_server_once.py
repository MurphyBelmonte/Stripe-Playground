import sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from financial_launcher import LauncherLogger, DependencyManager, ServerManager
import os

log = LauncherLogger()
dm = DependencyManager(log)
sm = ServerManager(log, dm)

# Force a non-default port to avoid conflicts during automated test
os.environ['FCC_PORT'] = os.environ.get('FCC_PORT', '8010')
if sm.start_server():
    print("Server reported started. Checking health...")
    import requests, urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    for _ in range(20):
        try:
            r = requests.get(f"{sm.server_url}/health", verify=False, timeout=3)
            print("HEALTH:", r.status_code, r.text[:200])
            break
        except Exception as e:
            print("waiting...", e)
            time.sleep(1)
    # If still not healthy, try to read server stderr/stdout for diagnostics
    if not sm.is_server_healthy():
        try:
            out, err = sm.server_process.communicate(timeout=5)
            print("SERVER STDOUT:\n", (out or b'').decode(errors='ignore')[-1000:])
            print("SERVER STDERR:\n", (err or b'').decode(errors='ignore')[-2000:])
        except Exception as e:
            print("Could not read process output:", e)
    # Stop server after check
    try:
        sm.stop_server()
    except Exception as e:
        print("stop error:", e)
else:
    print("Server failed to start.")
