"""
Random metadata generation for video uploads
"""
import random
from typing import List
from faker import Faker

from .config import config
from .logger import log


class MetadataGenerator:
    """Generates random titles, descriptions, and tags for videos"""
    
    def __init__(self):
        """Initialize the metadata generator"""
        self.fake = Faker()
        
        # Predefined title templates
        self.title_templates = [
            "Amazing Video #{number}",
            "Epic Content - {adjective} {noun}",
            "Must Watch: {adjective} {noun}",
            "Incredible {noun} Compilation",
            "Best {adjective} {noun} Ever",
            "Awesome {noun} Collection",
            "Ultimate {adjective} Experience",
            "Fantastic {noun} Showcase",
            "Spectacular {adjective} Moments",
            "Outstanding {noun} Highlights",
            "Random Upload #{number}",
            "Video Content - {date}",
            "Daily Upload #{number}",
            "Fresh {adjective} Content",
            "New {noun} Video"
        ]
        
        # Adjectives for titles
        self.adjectives = [
            "Amazing", "Incredible", "Awesome", "Fantastic", "Spectacular",
            "Outstanding", "Brilliant", "Magnificent", "Wonderful", "Excellent",
            "Superb", "Marvelous", "Extraordinary", "Remarkable", "Stunning",
            "Epic", "Ultimate", "Perfect", "Legendary", "Phenomenal"
        ]
        
        # Nouns for titles
        self.nouns = [
            "Video", "Content", "Footage", "Clip", "Recording", "Film",
            "Movie", "Show", "Episode", "Segment", "Compilation", "Collection",
            "Highlights", "Moments", "Scenes", "Action", "Adventure", "Journey",
            "Experience", "Story", "Documentary", "Tutorial", "Guide", "Review"
        ]
        
        # Description templates
        self.description_templates = [
            "This is an amazing video that you definitely need to watch! {sentence1} {sentence2} Don't forget to like and subscribe!",
            "Welcome to this incredible content! {sentence1} {sentence2} Hope you enjoy watching!",
            "Check out this awesome video! {sentence1} {sentence2} Thanks for watching!",
            "Here's some fantastic content for you! {sentence1} {sentence2} Please share if you like it!",
            "This video contains some really interesting stuff. {sentence1} {sentence2} Let me know what you think!",
            "Another great upload for your entertainment! {sentence1} {sentence2} Stay tuned for more!",
            "Fresh content just for you! {sentence1} {sentence2} Don't miss out on future uploads!",
            "Quality video content that's worth your time. {sentence1} {sentence2} Enjoy the show!",
            "Here's something special I wanted to share. {sentence1} {sentence2} Hope it brightens your day!",
            "New video alert! {sentence1} {sentence2} Thanks for being part of the community!"
        ]
        
        # Common video tags
        self.common_tags = [
            "video", "content", "entertainment", "fun", "awesome", "amazing",
            "cool", "interesting", "viral", "trending", "popular", "best",
            "new", "fresh", "daily", "upload", "channel", "subscribe",
            "like", "share", "watch", "enjoy", "quality", "hd", "original",
            "creative", "unique", "special", "exclusive", "premium", "top"
        ]
        
        # Category-specific tags
        self.category_tags = {
            "gaming": ["gaming", "games", "gameplay", "gamer", "play", "stream", "esports"],
            "music": ["music", "song", "audio", "sound", "beat", "melody", "rhythm"],
            "comedy": ["funny", "comedy", "humor", "laugh", "joke", "hilarious", "meme"],
            "education": ["learn", "tutorial", "guide", "howto", "education", "tips", "knowledge"],
            "tech": ["technology", "tech", "gadget", "review", "unboxing", "demo", "innovation"],
            "lifestyle": ["lifestyle", "vlog", "daily", "life", "personal", "routine", "experience"],
            "sports": ["sports", "fitness", "workout", "training", "athlete", "competition", "game"],
            "travel": ["travel", "adventure", "explore", "journey", "destination", "vacation", "trip"]
        }
        
        log.info("MetadataGenerator initialized")
    
    def generate_title(self) -> str:
        """Generate a random video title"""
        try:
            template = random.choice(self.title_templates)
            
            # Replace placeholders
            title = template.format(
                number=random.randint(1, 9999),
                adjective=random.choice(self.adjectives),
                noun=random.choice(self.nouns),
                date=self.fake.date()
            )
            
            log.debug(f"Generated title: {title}")
            return title
            
        except Exception as e:
            log.error(f"Error generating title: {e}")
            return f"Random Upload #{random.randint(1, 9999)}"
    
    def generate_description(self) -> str:
        """Generate a random video description"""
        try:
            template = random.choice(self.description_templates)
            
            # Generate random sentences
            sentence1 = self.fake.sentence()
            sentence2 = self.fake.sentence()
            
            description = template.format(
                sentence1=sentence1,
                sentence2=sentence2
            )
            
            log.debug(f"Generated description: {description[:50]}...")
            return description
            
        except Exception as e:
            log.error(f"Error generating description: {e}")
            return "This is an awesome video! Hope you enjoy watching. Thanks for your support!"
    
    def generate_tags(self, count: int = None, category: str = None) -> List[str]:
        """
        Generate random tags for video
        
        Args:
            count: Number of tags to generate (default: random 3-8)
            category: Specific category for tags (optional)
            
        Returns:
            List of tags
        """
        try:
            if count is None:
                count = random.randint(3, 8)
            
            tags = []
            
            # Add common tags
            common_count = min(count // 2, 4)
            tags.extend(random.sample(self.common_tags, common_count))
            
            # Add category-specific tags if specified
            if category and category in self.category_tags:
                category_count = min(count - len(tags), 3)
                tags.extend(random.sample(self.category_tags[category], category_count))
            
            # Fill remaining with random common tags or fake words
            while len(tags) < count:
                if random.choice([True, False]):
                    # Add another common tag
                    tag = random.choice(self.common_tags)
                    if tag not in tags:
                        tags.append(tag)
                else:
                    # Add a fake word
                    fake_tag = self.fake.word().lower()
                    if fake_tag not in tags and len(fake_tag) > 2:
                        tags.append(fake_tag)
            
            # Ensure we don't exceed the count
            tags = tags[:count]
            
            log.debug(f"Generated tags: {tags}")
            return tags
            
        except Exception as e:
            log.error(f"Error generating tags: {e}")
            return ["video", "content", "awesome", "watch", "subscribe"]
    
    def generate_complete_metadata(self, category: str = None) -> dict:
        """
        Generate complete metadata set (title, description, tags)
        
        Args:
            category: Optional category for targeted content
            
        Returns:
            Dict with title, description, and tags
        """
        try:
            metadata = {
                "title": self.generate_title(),
                "description": self.generate_description(),
                "tags": self.generate_tags(category=category)
            }
            
            log.info(f"Generated complete metadata for category: {category}")
            return metadata
            
        except Exception as e:
            log.error(f"Error generating complete metadata: {e}")
            return {
                "title": f"Random Upload #{random.randint(1, 9999)}",
                "description": "This is an awesome video! Hope you enjoy watching.",
                "tags": ["video", "content", "awesome"]
            }
    
    def customize_metadata(self, base_title: str = None, base_description: str = None, 
                          base_tags: List[str] = None) -> dict:
        """
        Customize existing metadata by enhancing it
        
        Args:
            base_title: Existing title to enhance
            base_description: Existing description to enhance  
            base_tags: Existing tags to enhance
            
        Returns:
            Enhanced metadata dict
        """
        try:
            # Enhance title
            if base_title:
                title = base_title
                # Add random adjective if title is short
                if len(title.split()) < 3:
                    adjective = random.choice(self.adjectives)
                    title = f"{adjective} {title}"
            else:
                title = self.generate_title()
            
            # Enhance description
            if base_description:
                description = base_description
                # Add call to action if missing
                if "subscribe" not in description.lower() and "like" not in description.lower():
                    description += " Don't forget to like and subscribe!"
            else:
                description = self.generate_description()
            
            # Enhance tags
            if base_tags:
                tags = list(base_tags)
                # Add some common tags if we have less than 5
                if len(tags) < 5:
                    additional_tags = random.sample(self.common_tags, 5 - len(tags))
                    tags.extend([tag for tag in additional_tags if tag not in tags])
            else:
                tags = self.generate_tags()
            
            metadata = {
                "title": title,
                "description": description,
                "tags": tags
            }
            
            log.info("Customized metadata successfully")
            return metadata
            
        except Exception as e:
            log.error(f"Error customizing metadata: {e}")
            return self.generate_complete_metadata()
