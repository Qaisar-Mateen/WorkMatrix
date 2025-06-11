import os
import sys
import time
import logging
from datetime import datetime
from typing import Optional, Tuple
import mss
from PIL import Image, ImageEnhance
from pathlib import Path

# Add the src directory to Python path for imports
if getattr(sys, 'frozen', False):
    # If running as executable
    base_dir = os.path.dirname(sys.executable)
    src_dir = os.path.join(base_dir, 'src')
else:
    # If running as script
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from utils.database import LocalDatabase
from config.screenshot_config import ScreenshotConfig

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

class ScreenshotCollector:
    def __init__(self, user_id: str, config: Optional[ScreenshotConfig] = None):
        """Initialize the screenshot collector."""
        self.user_id = user_id
        self.config = config or ScreenshotConfig()
        self.db = LocalDatabase()
        self.is_running = False
        self.sct = mss.mss()
        
        # Create screenshots directory
        self.screenshots_dir = self._get_screenshots_directory()
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        logger.info(f"ScreenshotCollector initialized for user: {user_id}")

    def _get_screenshots_directory(self) -> str:
        """Get the screenshots directory path."""
        if getattr(sys, 'frozen', False):
            # If running as executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running as script
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        return os.path.join(base_dir, 'data', 'screenshots')

    def start_collection(self):
        """Start the screenshot collection process."""
        self.is_running = True
        logger.info("Screenshot collection started")
        
        while self.is_running:
            try:
                self.capture_screenshot()
                time.sleep(self.config.interval)
            except Exception as e:
                logger.error(f"Error in screenshot collection loop: {str(e)}")
                time.sleep(5)  # Wait a bit before retrying

    def stop_collection(self):
        """Stop the screenshot collection process."""
        self.is_running = False
        logger.info("Screenshot collection stopped")

    def capture_screenshot(self) -> Optional[str]:
        """Capture a screenshot and save it."""
        try:
            # Take screenshot
            screenshot = self.sct.grab(self.sct.monitors[0])  # Primary monitor
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
            # Apply compression if needed
            if self.config.compression_quality < 100:
                img = self._apply_compression(img)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}_{self.user_id}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Save image
            img.save(filepath, "PNG", optimize=True)
            
            # Store in database
            screenshot_id = self.db.insert_screenshot(self.user_id, filepath)
            
            logger.info(f"Screenshot captured: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error capturing screenshot: {str(e)}")
            return None

    def _apply_compression(self, img: Image.Image) -> Image.Image:
        """Apply compression to the image."""
        try:
            # Resize if needed
            if self.config.max_width or self.config.max_height:
                img = self._resize_image(img)
            
            # Adjust quality by reducing colors or enhancing
            if self.config.compression_quality < 80:
                # Convert to RGB if not already
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Reduce quality by adjusting brightness/contrast slightly
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(0.95)
            
            return img
            
        except Exception as e:
            logger.error(f"Error applying compression: {str(e)}")
            return img

    def _resize_image(self, img: Image.Image) -> Image.Image:
        """Resize image based on configuration."""
        try:
            width, height = img.size
            
            # Calculate new dimensions
            if self.config.max_width and width > self.config.max_width:
                ratio = self.config.max_width / width
                new_width = self.config.max_width
                new_height = int(height * ratio)
            else:
                new_width, new_height = width, height
            
            if self.config.max_height and new_height > self.config.max_height:
                ratio = self.config.max_height / new_height
                new_width = int(new_width * ratio)
                new_height = self.config.max_height
            
            if new_width != width or new_height != height:
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"Image resized from {width}x{height} to {new_width}x{new_height}")
            
            return img
            
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            return img

    def cleanup_old_screenshots(self, days: int = 7):
        """Clean up old screenshot files."""
        try:
            deleted_count = self.db.delete_old_media("screenshots", self.screenshots_dir, days)
            logger.info(f"Cleaned up {deleted_count} old screenshots")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old screenshots: {str(e)}")
            return 0

    def get_screenshot_stats(self) -> dict:
        """Get statistics about screenshots."""
        try:
            stats = {
                'total_files': 0,
                'total_size_mb': 0,
                'oldest_file': None,
                'newest_file': None
            }
            
            if os.path.exists(self.screenshots_dir):
                files = list(Path(self.screenshots_dir).glob("*.png"))
                stats['total_files'] = len(files)
                
                if files:
                    total_size = sum(f.stat().st_size for f in files)
                    stats['total_size_mb'] = round(total_size / 1024 / 1024, 2)
                    
                    # Get oldest and newest files
                    files_with_time = [(f, f.stat().st_mtime) for f in files]
                    files_with_time.sort(key=lambda x: x[1])
                    
                    stats['oldest_file'] = files_with_time[0][0].name
                    stats['newest_file'] = files_with_time[-1][0].name
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting screenshot stats: {str(e)}")
            return {}

    def get_recent_screenshots(self, limit: int = 10) -> list:
        """Get a list of recent screenshots."""
        try:
            if not os.path.exists(self.screenshots_dir):
                return []
            
            files = list(Path(self.screenshots_dir).glob("*.png"))
            files_with_time = [(f, f.stat().st_mtime) for f in files]
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            
            recent_files = []
            for file_path, mtime in files_with_time[:limit]:
                recent_files.append({
                    'filename': file_path.name,
                    'filepath': str(file_path),
                    'size_mb': round(file_path.stat().st_size / 1024 / 1024, 2),
                    'created_at': datetime.fromtimestamp(mtime).isoformat()
                })
            
            return recent_files
            
        except Exception as e:
            logger.error(f"Error getting recent screenshots: {str(e)}")
            return []

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            if hasattr(self, 'sct'):
                self.sct.close()
        except:
            pass