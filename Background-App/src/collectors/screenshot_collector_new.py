import os
import time
import logging
import mss
import mss.tools
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from PIL import Image
import io
import shutil

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database import LocalDatabase

# Configure logging
def setup_screenshot_logging():
    # Get the directory where the executable is located  
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    log_dir = os.path.join(base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'screenshot.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

setup_screenshot_logging()
logger = logging.getLogger(__name__)

class ScreenshotSettings:
    def __init__(self):
        self.interval = 300  # 5 minutes
        self.compression = True
        self.quality = 60
        self.capture_all_monitors = False
        self.max_storage_mb = 500
        self.retention_days = 7
        self.privacy_mode = False
        self.excluded_apps = []
        self.excluded_windows = []

    def get_max_storage_bytes(self):
        return self.max_storage_mb * 1024 * 1024

    def is_app_excluded(self, app_name):
        return app_name.lower() in [app.lower() for app in self.excluded_apps]

    def is_window_excluded(self, window_title):
        return any(excluded.lower() in window_title.lower() for excluded in self.excluded_windows)

class EventManager:
    def __init__(self):
        pass
    
    def emit(self, event_name, data):
        logger.info(f"Event emitted: {event_name}")
    
    def close(self):
        pass

class ScreenshotCollector:
    def __init__(self, user_id: str, settings: Optional[ScreenshotSettings] = None):
        self.user_id = user_id
        self.settings = settings or ScreenshotSettings()
        self.db = LocalDatabase()
        self.event_manager = EventManager()
        
        # Set up directories
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.screenshot_dir = Path(base_dir) / "data" / "screenshots" / user_id
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        self.last_screenshot_time = 0
        self.failed_attempts = 0
        self.max_failed_attempts = 3
        self.logger.info(f"Screenshot collector initialized for user {user_id}")

    def _check_storage_space(self) -> Tuple[bool, str]:
        """Check if there's enough storage space for new screenshots."""
        try:
            total_size = sum(f.stat().st_size for f in self.screenshot_dir.rglob('*') if f.is_file())
            max_size = self.settings.get_max_storage_bytes()
            
            if total_size >= max_size:
                return False, f"Storage limit reached ({total_size / (1024**3):.2f}GB used)"
            return True, ""
        except Exception as e:
            self.logger.error(f"Error checking storage space: {str(e)}")
            return False, str(e)

    def _should_capture(self, app_name: str, window_title: str) -> Tuple[bool, str]:
        """Determine if a screenshot should be captured based on settings."""
        if not self.settings.privacy_mode:
            return True, ""
            
        if self.settings.is_app_excluded(app_name):
            return False, f"App excluded: {app_name}"
            
        if self.settings.is_window_excluded(window_title):
            return False, f"Window excluded: {window_title}"
            
        return True, ""

    def _compress_image(self, image_data: bytes, quality: int = None) -> bytes:
        """Compress image data if compression is enabled."""
        if not self.settings.compression:
            return image_data
            
        try:
            quality = quality or self.settings.quality
            img = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
                
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue()
        except Exception as e:
            self.logger.error(f"Error compressing image: {str(e)}")
            return image_data

    def _get_monitor_info(self) -> List[Dict]:
        """Get information about available monitors."""
        try:
            with mss.mss() as sct:
                monitors = []
                for i, monitor in enumerate(sct.monitors[1:], 1):  # Skip the "all monitors" monitor
                    monitors.append({
                        "id": i,
                        "left": monitor["left"],
                        "top": monitor["top"],
                        "width": monitor["width"],
                        "height": monitor["height"]
                    })
                return monitors
        except Exception as e:
            self.logger.error(f"Error getting monitor info: {str(e)}")
            return []

    def capture_screenshot(self, app_name: str = "", window_title: str = "") -> Optional[Dict]:
        """Capture a screenshot if conditions are met."""
        current_time = time.time()
        
        # Check interval
        if current_time - self.last_screenshot_time < self.settings.interval:
            return None
            
        # Check storage space
        has_space, space_msg = self._check_storage_space()
        if not has_space:
            self.logger.warning(f"Skipping screenshot: {space_msg}")
            return None
            
        # Check privacy settings
        should_capture, reason = self._should_capture(app_name, window_title)
        if not should_capture:
            self.logger.info(f"Skipping screenshot: {reason}")
            return None

        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.jpg"
            filepath = self.screenshot_dir / filename

            # Capture screenshot
            with mss.mss() as sct:
                screenshots = []
                if self.settings.capture_all_monitors:
                    # Capture all monitors
                    for i, monitor in enumerate(sct.monitors[1:], 1):
                        screenshot = sct.grab(monitor)
                        img_data = mss.tools.to_png(screenshot.rgb, screenshot.size)
                        if self.settings.compression:
                            img_data = self._compress_image(img_data)
                        screenshots.append({
                            "monitor": i,
                            "data": img_data,
                            "size": screenshot.size
                        })
                else:
                    # Capture primary monitor
                    monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                    screenshot = sct.grab(monitor)
                    img_data = mss.tools.to_png(screenshot.rgb, screenshot.size)
                    if self.settings.compression:
                        img_data = self._compress_image(img_data)
                    screenshots.append({
                        "monitor": 1,
                        "data": img_data,
                        "size": screenshot.size
                    })

                # Save screenshots and create records
                for i, screenshot_info in enumerate(screenshots):
                    if len(screenshots) > 1:
                        monitor_filename = f"screenshot_{timestamp}_monitor{i+1}.jpg"
                    else:
                        monitor_filename = filename
                        
                    monitor_filepath = self.screenshot_dir / monitor_filename
                    with open(monitor_filepath, 'wb') as f:
                        f.write(screenshot_info["data"])

                    # Create screenshot data
                    screenshot_data = {
                        "user_id": self.user_id,
                        "filename": monitor_filename,
                        "filepath": str(monitor_filepath),
                        "timestamp": datetime.now().isoformat(),
                        "monitor": screenshot_info["monitor"],
                        "size": screenshot_info["size"],
                        "app_name": app_name,
                        "window_title": window_title,
                        "compressed": self.settings.compression,
                        "quality": self.settings.quality
                    }

                    # Store in local database
                    self.db.insert_screenshot(self.user_id, str(monitor_filepath))
                    
                    # Emit event
                    self.event_manager.emit("screenshot_captured", screenshot_data)
            
            # Update last screenshot time and reset failed attempts
            self.last_screenshot_time = current_time
            self.failed_attempts = 0

            self.logger.info(f"Screenshot captured: {filename}")
            return screenshot_data

        except Exception as e:
            self.failed_attempts += 1
            self.logger.error(f"Error capturing screenshot: {str(e)}")
            
            if self.failed_attempts >= self.max_failed_attempts:
                self.logger.error("Maximum failed attempts reached. Stopping screenshot capture.")
                self.event_manager.emit("screenshot_error", {
                    "user_id": self.user_id,
                    "error": str(e),
                    "failed_attempts": self.failed_attempts
                })
            
            return None

    def get_recent_screenshots(self, limit: int = 10) -> List[Dict]:
        """Get list of recent screenshots with metadata."""
        try:
            screenshots = []
            for file in sorted(self.screenshot_dir.glob("*.jpg"), reverse=True)[:limit]:
                try:
                    with Image.open(file) as img:
                        screenshots.append({
                            "filename": file.name,
                            "path": str(file),
                            "size": file.stat().st_size,
                            "dimensions": img.size,
                            "created": datetime.fromtimestamp(file.stat().st_ctime).isoformat()
                        })
                except Exception as e:
                    self.logger.error(f"Error reading screenshot {file}: {str(e)}")
            return screenshots
        except Exception as e:
            self.logger.error(f"Error getting recent screenshots: {str(e)}")
            return []

    def cleanup_old_screenshots(self) -> None:
        """Clean up screenshots based on retention policy."""
        try:
            self.db.delete_old_media("screenshots", str(self.screenshot_dir), 
                                   self.settings.retention_days)
            self.logger.info(f"Cleaned up screenshots older than {self.settings.retention_days} days")
        except Exception as e:
            self.logger.error(f"Error cleaning up screenshots: {str(e)}")
            raise

    def get_storage_usage(self) -> Dict:
        """Get current storage usage statistics."""
        try:
            total_size = sum(f.stat().st_size for f in self.screenshot_dir.rglob('*') if f.is_file())
            max_size = self.settings.get_max_storage_bytes()
            file_count = sum(1 for f in self.screenshot_dir.rglob('*') if f.is_file())
            
            return {
                "total_size_bytes": total_size,
                "total_size_gb": total_size / (1024**3),
                "max_size_bytes": max_size,
                "max_size_gb": max_size / (1024**3),
                "file_count": file_count,
                "usage_percent": (total_size / max_size) * 100 if max_size > 0 else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting storage usage: {str(e)}")
            return {
                "total_size_bytes": 0,
                "total_size_gb": 0,
                "max_size_bytes": 0,
                "max_size_gb": 0,
                "file_count": 0,
                "usage_percent": 0
            }

    def close(self) -> None:
        """Clean up resources."""
        try:
            self.db.close()
            self.event_manager.close()
            self.logger.info("Screenshot collector closed")
        except Exception as e:
            self.logger.error(f"Error closing screenshot collector: {str(e)}")
            raise
