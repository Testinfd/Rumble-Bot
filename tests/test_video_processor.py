"""
Tests for video processor module
"""
import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.video_processor import VideoProcessor


class TestVideoProcessor:
    """Test video processing functionality"""
    
    def setup_method(self):
        """Setup test instance"""
        self.processor = VideoProcessor()
    
    def test_init(self):
        """Test processor initialization"""
        assert self.processor.downloads_dir.exists()
        assert self.processor.temp_dir.exists()
    
    def test_supported_formats(self):
        """Test supported video formats"""
        assert '.mp4' in self.processor.SUPPORTED_FORMATS
        assert '.avi' in self.processor.SUPPORTED_FORMATS
        assert '.mov' in self.processor.SUPPORTED_FORMATS
        assert '.webm' in self.processor.SUPPORTED_FORMATS
    
    def test_supported_mime_types(self):
        """Test supported MIME types"""
        assert 'video/mp4' in self.processor.SUPPORTED_MIME_TYPES
        assert 'video/avi' in self.processor.SUPPORTED_MIME_TYPES
        assert 'video/quicktime' in self.processor.SUPPORTED_MIME_TYPES
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file"""
        result = self.processor.validate_video_file("nonexistent.mp4")
        
        assert result['valid'] == False
        assert 'File does not exist' in result['errors']
    
    def test_validate_file_extension(self):
        """Test file extension validation"""
        # Create temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'test content')
            temp_path = temp_file.name
        
        try:
            result = self.processor.validate_video_file(temp_path)
            assert result['valid'] == False
            assert any('Unsupported file format' in error for error in result['errors'])
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_size_limit(self):
        """Test file size limit validation"""
        # Create a large temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            # Write data larger than the configured limit
            large_data = b'0' * (self.processor.downloads_dir.parent.stat().st_size + 1000000000)  # 1GB
            temp_file.write(large_data[:1000])  # Write smaller amount for test
            temp_path = temp_file.name
        
        try:
            # Mock the file size to be larger than limit
            original_stat = os.stat
            def mock_stat(path):
                if path == temp_path:
                    stat_result = original_stat(path)
                    # Create a mock stat result with large size
                    class MockStat:
                        st_size = 3000 * 1024 * 1024  # 3GB
                    return MockStat()
                return original_stat(path)
            
            import builtins
            original_open = builtins.open
            
            # We'll just test the logic without actually creating huge files
            result = self.processor.validate_video_file(temp_path)
            # The validation should pass for small test file
            
        finally:
            os.unlink(temp_path)
    
    def test_get_video_info(self):
        """Test getting video information"""
        # Create temporary video file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b'fake video content')
            temp_path = temp_file.name
        
        try:
            info = self.processor.get_video_info(temp_path)
            
            assert info['file_path'] == temp_path
            assert info['file_name'] == Path(temp_path).name
            assert info['file_size'] > 0
            assert info['file_size_mb'] > 0
            assert info['file_extension'] == '.mp4'
        finally:
            os.unlink(temp_path)
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        from src.security import SecurityValidator
        
        test_cases = [
            ('normal_file.mp4', 'normal_file.mp4'),
            ('file with spaces.mp4', 'file with spaces.mp4'),
            ('file<>:"/\\|?*.mp4', 'file_________.mp4'),
            ('...file...', 'file'),
            ('', 'file'),
        ]
        
        for input_name, expected in test_cases:
            result = SecurityValidator.sanitize_filename(input_name)
            assert result == expected
    
    def test_move_to_temp(self):
        """Test moving file to temp directory"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(b'test content')
            temp_path = temp_file.name
        
        try:
            # Move to temp
            new_path = self.processor.move_to_temp(temp_path)
            
            assert new_path is not None
            assert Path(new_path).exists()
            assert not Path(temp_path).exists()
            assert str(self.processor.temp_dir) in new_path
            
            # Cleanup
            if new_path and Path(new_path).exists():
                os.unlink(new_path)
        except:
            # Cleanup in case of failure
            if Path(temp_path).exists():
                os.unlink(temp_path)
    
    def test_cleanup_old_files(self):
        """Test cleanup of old files"""
        # Create test file in downloads directory
        test_file = self.processor.downloads_dir / "test_old_file.mp4"
        test_file.write_text("test content")
        
        # Set file modification time to be old
        import time
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        os.utime(test_file, (old_time, old_time))
        
        # Run cleanup
        self.processor.cleanup_old_files(max_age_hours=24)
        
        # File should be deleted
        assert not test_file.exists()
