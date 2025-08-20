"""
Tests for metadata generator module
"""
import pytest
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.metadata_generator import MetadataGenerator


class TestMetadataGenerator:
    """Test metadata generation functionality"""
    
    def setup_method(self):
        """Setup test instance"""
        self.generator = MetadataGenerator()
    
    def test_generate_title(self):
        """Test title generation"""
        title = self.generator.generate_title()
        
        assert isinstance(title, str)
        assert len(title) > 0
        assert len(title) < 200  # Reasonable title length
    
    def test_generate_description(self):
        """Test description generation"""
        description = self.generator.generate_description()
        
        assert isinstance(description, str)
        assert len(description) > 10
        assert len(description) < 1000  # Reasonable description length
    
    def test_generate_tags(self):
        """Test tag generation"""
        tags = self.generator.generate_tags()
        
        assert isinstance(tags, list)
        assert len(tags) >= 3
        assert len(tags) <= 8
        assert all(isinstance(tag, str) for tag in tags)
        assert all(len(tag) > 0 for tag in tags)
    
    def test_generate_tags_with_count(self):
        """Test tag generation with specific count"""
        count = 5
        tags = self.generator.generate_tags(count=count)
        
        assert len(tags) == count
    
    def test_generate_tags_with_category(self):
        """Test tag generation with category"""
        category = "gaming"
        tags = self.generator.generate_tags(category=category)
        
        # Should contain at least one gaming-related tag
        gaming_tags = self.generator.category_tags[category]
        assert any(tag in gaming_tags for tag in tags)
    
    def test_generate_complete_metadata(self):
        """Test complete metadata generation"""
        metadata = self.generator.generate_complete_metadata()
        
        assert isinstance(metadata, dict)
        assert 'title' in metadata
        assert 'description' in metadata
        assert 'tags' in metadata
        
        assert isinstance(metadata['title'], str)
        assert isinstance(metadata['description'], str)
        assert isinstance(metadata['tags'], list)
    
    def test_customize_metadata_with_base_title(self):
        """Test metadata customization with base title"""
        base_title = "Test Video"
        metadata = self.generator.customize_metadata(base_title=base_title)
        
        assert base_title in metadata['title']
    
    def test_customize_metadata_with_base_description(self):
        """Test metadata customization with base description"""
        base_description = "This is a test video"
        metadata = self.generator.customize_metadata(base_description=base_description)
        
        assert base_description in metadata['description']
    
    def test_customize_metadata_with_base_tags(self):
        """Test metadata customization with base tags"""
        base_tags = ["test", "video"]
        metadata = self.generator.customize_metadata(base_tags=base_tags)
        
        # Should contain original tags
        for tag in base_tags:
            assert tag in metadata['tags']
    
    def test_title_templates_not_empty(self):
        """Test that title templates are not empty"""
        assert len(self.generator.title_templates) > 0
        assert all(isinstance(template, str) for template in self.generator.title_templates)
    
    def test_adjectives_not_empty(self):
        """Test that adjectives list is not empty"""
        assert len(self.generator.adjectives) > 0
        assert all(isinstance(adj, str) for adj in self.generator.adjectives)
    
    def test_nouns_not_empty(self):
        """Test that nouns list is not empty"""
        assert len(self.generator.nouns) > 0
        assert all(isinstance(noun, str) for noun in self.generator.nouns)
    
    def test_common_tags_not_empty(self):
        """Test that common tags list is not empty"""
        assert len(self.generator.common_tags) > 0
        assert all(isinstance(tag, str) for tag in self.generator.common_tags)
    
    def test_category_tags_structure(self):
        """Test category tags structure"""
        assert isinstance(self.generator.category_tags, dict)
        assert len(self.generator.category_tags) > 0
        
        for category, tags in self.generator.category_tags.items():
            assert isinstance(category, str)
            assert isinstance(tags, list)
            assert len(tags) > 0
            assert all(isinstance(tag, str) for tag in tags)
