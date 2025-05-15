
import sys
import random
import logging
import os
import string
from typing import Dict, Any, List, Optional, Union

__version__ = "0.1.1"
__updated__ = "2025-05-15"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "emotional_character_generator.log"))
    ]
)
logger = logging.getLogger("emotional_character_generator")

# Import MCP server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("emotional-character-generator-server")

# Define the canonical set of emotions
EMOTIONS = [
    "Joy", 
    "Trust", 
    "Fear", 
    "Surprise", 
    "Sadness", 
    "Boredom", 
    "Anger", 
    "Interest"
]

# Define a list of character name prefixes and suffixes for procedural generation
NAME_PREFIXES = [
    "Ar", "Br", "Cr", "Dr", "El", "Fr", "Gr", "Ha", "In", "Ja", 
    "Ka", "Li", "Mo", "Ne", "Ori", "Pi", "Qu", "Ra", "Se", "Tr", 
    "Ul", "Vi", "Wa", "Xe", "Yu", "Za"
]

NAME_SUFFIXES = [
    "ack", "ber", "cor", "dor", "ek", "fin", "gon", "hel", "il", "jin",
    "kin", "lar", "mor", "nir", "ond", "pex", "rin", "sar", "tor", "ven",
    "wix", "xar", "yll", "zor"
]

# Define character trait pools
TRAITS = [
    "Brave", "Cautious", "Clever", "Determined", "Empathetic", 
    "Forgiving", "Generous", "Honest", "Impulsive", "Judgmental",
    "Kind", "Loyal", "Mysterious", "Nurturing", "Observant", 
    "Practical", "Quiet", "Resourceful", "Stubborn", "Thoughtful"
]

QUIRKS = [
    "Always hums when thinking", "Blinks rapidly when nervous", 
    "Collects odd trinkets", "Doodles in the margins", 
    "Eats one food at a time", "Fidgets with a coin", 
    "Gestures wildly while talking", "Has perfect pitch",
    "Interrupts with 'actually' frequently", "Jumps at loud noises",
    "Keeps a journal of dreams", "Laughs at inappropriate times",
    "Memorizes obscure facts", "Never uses contractions",
    "Only wears one color", "Prefers the night", 
    "Quotes ancient proverbs", "Repeats the last word spoken",
    "Speaks to inanimate objects", "Twirls hair when lying"
]

# Function to generate a character name
def generate_character_name():
    prefix = random.choice(NAME_PREFIXES)
    suffix = random.choice(NAME_SUFFIXES)
    return f"{prefix}{suffix}"

# Function to generate emotional narrative
def generate_emotional_narrative(primary, secondary, name, trait):
    """Generate a short narrative based on the character's emotions."""
    
    # Map emotions to narrative templates
    emotion_templates = {
        "Joy": [
            f"{name} radiates warmth and positivity, finding delight in the smallest things.",
            f"The world seems brighter through {name}'s eyes, as they embrace each moment with enthusiasm."
        ],
        "Trust": [
            f"With an open heart, {name} approaches others without reservation or suspicion.",
            f"{name} builds connections easily, offering reliability and steadfast support."
        ],
        "Fear": [
            f"Shadows seem to follow {name}, whose eyes constantly scan for unseen threats.",
            f"Behind {name}'s cautious demeanor lies a mind mapping every possible danger."
        ],
        "Surprise": [
            f"{name} lives in a state of constant wonder, easily amazed by the unexpected.",
            f"The world never ceases to astonish {name}, whose perspective shifts with each new discovery."
        ],
        "Sadness": [
            f"A melancholy aura surrounds {name}, who carries an invisible weight on their shoulders.",
            f"{name} finds beauty in sorrow, connecting deeply with the bittersweet nature of existence."
        ],
        "Boredom": [
            f"Nothing seems to hold {name}'s interest for long, as they search for something truly engaging.",
            f"{name} moves through life with detached indifference, waiting for something worthy of attention."
        ],
        "Anger": [
            f"Passion burns intensely within {name}, whose emotions simmer just below the surface.",
            f"{name} channels their fierce energy into every pursuit, driven by an inner fire."
        ],
        "Interest": [
            f"Curiosity guides {name}'s journey, as they explore the world with insatiable fascination.",
            f"{name} approaches everything with analytical focus, collecting knowledge like precious gems."
        ]
    }
    
    # Select a random template for the primary emotion
    primary_narrative = random.choice(emotion_templates[primary])
    
    # Create secondary emotion influence
    if primary != secondary:
        # If emotions are different, create a contrast
        secondary_templates = {
            "Joy": f"Yet beneath this {trait.lower()} exterior, unexpected moments of delight break through.",
            "Trust": f"Despite everything, {name} maintains a surprising willingness to believe in others.",
            "Fear": f"However, an undercurrent of anxiety influences many of {name}'s decisions.",
            "Surprise": f"At times, {name}'s perspective shifts dramatically when confronted with the unexpected.",
            "Sadness": f"In quiet moments, a profound melancholy reveals the depth of {name}'s character.",
            "Boredom": f"Still, {name} often finds themselves unimpressed by what others find captivating.",
            "Anger": f"When provoked, {name} reveals a fierce intensity that transforms their demeanor.",
            "Interest": f"Nevertheless, {name}'s attention is quickly captured by intriguing new concepts."
        }
        secondary_narrative = secondary_templates[secondary]
    else:
        # If primary and secondary are the same, intensify the primary
        intensifiers = {
            "Joy": f"This overwhelming positivity defines {name}'s very essence.",
            "Trust": f"This profound faith in others is the cornerstone of {name}'s worldview.",
            "Fear": f"This pervasive anxiety colors every aspect of {name}'s existence.",
            "Surprise": f"This perpetual astonishment defines how {name} experiences reality.",
            "Sadness": f"This deep-seated melancholy has become inseparable from {name}'s identity.",
            "Boredom": f"This chronic disinterest has become {name}'s defining characteristic.",
            "Anger": f"This smoldering intensity is fundamental to understanding {name}'s nature.",
            "Interest": f"This relentless curiosity is the driving force behind all {name} does."
        }
        secondary_narrative = intensifiers[primary]
    
    # Combine narratives
    return f"{primary_narrative} {secondary_narrative}"

@mcp.tool()
async def emotional_character_generator(
    count: int = 1,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generates random characters with primary and secondary emotions.
    
    Args:
        count: Number of characters to generate (default: 1)
        seed: Optional seed for the random generator for reproducible results
        
    Returns:
        Dictionary with generated characters and their emotional states
    """
    logger.info(f"Emotional character generator called with: count={count}, seed={seed}")
    
    # Set seed if provided
    if seed is not None:
        random.seed(seed)
        logger.info(f"Using seed: {seed}")
    
    # Validate count
    if count < 1:
        logger.warning(f"Invalid count: {count}, using 1 instead")
        count = 1
    elif count > 100:
        logger.warning(f"Count too large: {count}, limiting to 100")
        count = 100
    
    # Initialize result
    result = {
        "success": True,
        "count": count,
        "seed": seed,
        "emotions_used": EMOTIONS,
        "characters": []
    }
    
    try:
        # Generate characters
        for i in range(count):
            char_id = f"CHAR_{i+1:03d}"
            char_name = generate_character_name()
            
            # Select random emotions
            primary_emotion = random.choice(EMOTIONS)
            secondary_emotion = random.choice(EMOTIONS)  # Can be the same as primary
            
            # Generate a random trait and quirk for additional flavor
            trait = random.choice(TRAITS)
            quirk = random.choice(QUIRKS)
            
            # Create character object
            character = {
                "id": char_id,
                "name": char_name,
                "emotional_state": {
                    "primary": primary_emotion,
                    "secondary": secondary_emotion
                },
                "trait": trait,
                "quirk": quirk
            }
            
            # Add a narrative flavor text based on the emotions
            emotional_narrative = generate_emotional_narrative(primary_emotion, secondary_emotion, char_name, trait)
            character["narrative"] = emotional_narrative
            
            # Add to results
            result["characters"].append(character)
            
        logger.info(f"Generated {count} characters with emotional states")
    
    except Exception as e:
        logger.error(f"Character generation failed: {str(e)}")
        return {
            "success": False,
            "error": "Character generation failed",
            "reason": str(e)
        }
    
    # Simplify single results
    if count == 1:
        result["character"] = result["characters"][0]
    
    return result

if __name__ == "__main__":
    logger.info("Starting Emotional Character Generator MCP server")
    mcp.run(transport='stdio')
