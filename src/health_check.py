"""
Health check endpoint for monitoring
"""
import time
import threading
from flask import Flask, jsonify
from typing import Dict, Any

from .config import config
from .logger import log
from .error_handler import error_handler


class HealthChecker:
    """Health check service for monitoring bot status"""
    
    def __init__(self):
        """Initialize health checker"""
        self.app = Flask(__name__)
        self.start_time = time.time()
        self.last_activity = time.time()
        self.status = "starting"
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health')
        def health():
            return jsonify(self.get_health_status())
        
        @self.app.route('/status')
        def status():
            return jsonify(self.get_detailed_status())
        
        @self.app.route('/metrics')
        def metrics():
            return jsonify(self.get_metrics())
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get basic health status"""
        uptime = time.time() - self.start_time
        
        return {
            "status": self.status,
            "uptime_seconds": round(uptime, 2),
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        uptime = time.time() - self.start_time
        last_activity_ago = time.time() - self.last_activity
        
        # Get error summary
        error_summary = error_handler.get_error_summary()
        
        return {
            "status": self.status,
            "uptime_seconds": round(uptime, 2),
            "last_activity_seconds_ago": round(last_activity_ago, 2),
            "configuration": {
                "max_file_size_mb": config.MAX_FILE_SIZE_MB,
                "headless_mode": config.HEADLESS_MODE,
                "retry_attempts": config.RETRY_ATTEMPTS,
                "log_level": config.LOG_LEVEL
            },
            "errors": {
                "total_errors": error_summary.get('total_errors', 0),
                "error_counts": error_summary.get('error_counts', {}),
                "is_healthy": error_handler.is_healthy()
            },
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for monitoring"""
        uptime = time.time() - self.start_time
        error_summary = error_handler.get_error_summary()
        
        return {
            "uptime_seconds": round(uptime, 2),
            "total_errors": error_summary.get('total_errors', 0),
            "error_rate": error_summary.get('total_errors', 0) / max(uptime / 3600, 1),  # errors per hour
            "last_activity_seconds_ago": round(time.time() - self.last_activity, 2),
            "memory_usage_mb": self._get_memory_usage(),
            "is_healthy": error_handler.is_healthy(),
            "timestamp": time.time()
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return round(memory_info.rss / 1024 / 1024, 2)
        except ImportError:
            return 0.0
        except Exception:
            return 0.0
    
    def update_status(self, status: str):
        """Update bot status"""
        self.status = status
        self.last_activity = time.time()
        log.debug(f"Health status updated: {status}")
    
    def record_activity(self):
        """Record bot activity"""
        self.last_activity = time.time()
    
    def start_server(self):
        """Start health check server in background thread"""
        def run_server():
            try:
                self.app.run(
                    host=config.HOST,
                    port=config.PORT,
                    debug=False,
                    use_reloader=False
                )
            except Exception as e:
                log.error(f"Health check server error: {e}")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        log.info(f"Health check server started on {config.HOST}:{config.PORT}")


# Global health checker instance
health_checker = HealthChecker()
