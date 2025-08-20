"""
Video processing utilities for Rumble Bot
"""
import os
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from .config import config
from .logger import log


class VideoProcessor:
    """Handles video file processing and validation"""
    
    # Supported video formats
    SUPPORTED_FORMATS = {
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', 
        '.mkv', '.m4v', '.3gp', '.ogv', '.ts', '.mts'
    }
    
    # Supported MIME types
    SUPPORTED_MIME_TYPES = {
        'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
        'video/x-flv', 'video/webm', 'video/x-matroska', 'video/3gpp',
        'video/ogg', 'video/mp2t', 'video/x-ms-wmv'
    }
    
    def __init__(self):
        """Initialize video processor"""
        self.downloads_dir = Path(config.DOWNLOADS_DIR)
        self.temp_dir = Path(config.TEMP_DIR)
        
        # Ensure directories exist
        self.downloads_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        log.info("VideoProcessor initialized")
    
    def validate_video_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate video file format, size, and properties
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Dict with validation results
        """
        result = {
            'valid': False,
            'file_path': file_path,
            'file_size': 0,
            'file_extension': '',
            'mime_type': '',
            'errors': []
        }
        
        try:
            file_path_obj = Path(file_path)
            
            # Check if file exists
            if not file_path_obj.exists():
                result['errors'].append("File does not exist")
                return result
            
            # Get file size
            file_size = file_path_obj.stat().st_size
            result['file_size'] = file_size
            
            # Check file size limit
            max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
            if file_size > max_size_bytes:
                result['errors'].append(f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds limit ({config.MAX_FILE_SIZE_MB} MB)")
                return result
            
            # Get file extension
            file_extension = file_path_obj.suffix.lower()
            result['file_extension'] = file_extension
            
            # Check file extension
            if file_extension not in self.SUPPORTED_FORMATS:
                result['errors'].append(f"Unsupported file format: {file_extension}")
            
            # Get MIME type
            mime_type = self._get_mime_type(file_path)
            result['mime_type'] = mime_type
            
            # Check MIME type
            if mime_type and not any(supported in mime_type for supported in self.SUPPORTED_MIME_TYPES):
                result['errors'].append(f"Unsupported MIME type: {mime_type}")
            
            # Check if file is actually a video (basic check)
            if not self._is_video_file(file_path):
                result['errors'].append("File does not appear to be a valid video")
            
            # If no errors, mark as valid
            if not result['errors']:
                result['valid'] = True
                log.info(f"Video file validated successfully: {file_path}")
            else:
                log.warning(f"Video validation failed for {file_path}: {result['errors']}")
            
        except Exception as e:
            result['errors'].append(f"Validation error: {str(e)}")
            log.error(f"Error validating video file {file_path}: {e}")
        
        return result
    
    def _get_mime_type(self, file_path: str) -> Optional[str]:
        """Get MIME type of file"""
        try:
            if HAS_MAGIC:
                # Use python-magic for more accurate detection
                mime_type = magic.from_file(file_path, mime=True)
                return mime_type
            else:
                # Fallback to mimetypes module
                mime_type, _ = mimetypes.guess_type(file_path)
                return mime_type
        except Exception as e:
            log.warning(f"Could not determine MIME type for {file_path}: {e}")
            return None
    
    def _is_video_file(self, file_path: str) -> bool:
        """Basic check if file is a video by reading file header"""
        try:
            with open(file_path, 'rb') as f:
                # Read first 12 bytes to check for common video file signatures
                header = f.read(12)
                
                # Common video file signatures
                video_signatures = [
                    b'\x00\x00\x00\x18ftypmp4',  # MP4
                    b'\x00\x00\x00\x20ftypmp4',  # MP4
                    b'\x00\x00\x00\x1cftypisom', # MP4/MOV
                    b'RIFF',  # AVI (first 4 bytes)
                    b'\x1aE\xdf\xa3',  # MKV/WebM
                    b'FLV',   # FLV
                    b'\x00\x00\x00\x14ftyp',  # QuickTime
                ]
                
                # Check for signatures
                for signature in video_signatures:
                    if header.startswith(signature):
                        return True
                
                # Additional check for AVI
                if header.startswith(b'RIFF') and b'AVI ' in header:
                    return True
                
                # If no signature matches, assume it might be valid
                # (some formats don't have clear signatures)
                return True
                
        except Exception as e:
            log.warning(f"Could not read file header for {file_path}: {e}")
            return True  # Assume valid if we can't check
    
    def get_video_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic video information
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Dict with video information
        """
        info = {
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'file_size': 0,
            'file_size_mb': 0,
            'file_extension': '',
            'mime_type': ''
        }
        
        try:
            file_path_obj = Path(file_path)
            
            if file_path_obj.exists():
                file_size = file_path_obj.stat().st_size
                info['file_size'] = file_size
                info['file_size_mb'] = round(file_size / 1024 / 1024, 2)
                info['file_extension'] = file_path_obj.suffix.lower()
                info['mime_type'] = self._get_mime_type(file_path) or 'unknown'
                
        except Exception as e:
            log.error(f"Error getting video info for {file_path}: {e}")
        
        return info
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old files from downloads and temp directories
        
        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        import time
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        directories = [self.downloads_dir, self.temp_dir]
        
        for directory in directories:
            try:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > max_age_seconds:
                            file_path.unlink()
                            log.info(f"Cleaned up old file: {file_path}")
            except Exception as e:
                log.error(f"Error cleaning up directory {directory}: {e}")
    
    def move_to_temp(self, file_path: str) -> Optional[str]:
        """
        Move file to temp directory
        
        Args:
            file_path: Source file path
            
        Returns:
            New file path in temp directory or None if failed
        """
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return None
            
            temp_path = self.temp_dir / source_path.name
            source_path.rename(temp_path)
            
            log.info(f"Moved file to temp: {temp_path}")
            return str(temp_path)
            
        except Exception as e:
            log.error(f"Error moving file to temp: {e}")
            return None
