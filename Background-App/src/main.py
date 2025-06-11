import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from services.websocket_server import start_websocket_server
from services.monitor_api import APIMonitor
from services.http_server import start_http_server

# load env vars from .env
load_dotenv()

def setup_logging():
    logger = logging.getLogger("workmatrix")
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'workmatrix.log')
    
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    
    fh = logging.FileHandler(log_file)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

logger = setup_logging()

async def main():
    logger.info("Booting WorkMatrix services…")

    # 1) WebSocket
    ws_task = asyncio.create_task(start_websocket_server())

    # 2) API monitor (might be sync or async)
    api_mon = APIMonitor()
    if asyncio.iscoroutinefunction(api_mon.run):
        api_task = asyncio.create_task(api_mon.run())
    else:
        # wrap the sync .run() in a thread so it won't block the loop
        api_task = asyncio.create_task(asyncio.to_thread(api_mon.run))

    # 3) HTTP server
    http_task = asyncio.create_task(start_http_server())

    # wait on all three
    await asyncio.gather(ws_task, api_task, http_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down on user interrupt")
        sys.exit(0)
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)
