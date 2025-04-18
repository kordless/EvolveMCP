import sys
import importlib.util
import subprocess
import logging
from typing import Dict, Any, List, Optional

# Configure logging to file instead of stdout to avoid interfering with MCP JSON communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("textanalyzer.log")]
)
logger = logging.getLogger("textanalyzer")

# This function checks if a package is installed and installs it if needed
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            logger.info(f"Installing {package_name}")
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            # Log pip output to file instead of printing to stdout
            for line in stdout.splitlines():
                logger.info(line)
            if stderr:
                for line in stderr.splitlines():
                    logger.warning(line)
                    
            if process.returncode == 0:
                logger.info(f"Successfully installed {package_name}")
                return True
            else:
                logger.error(f"Failed to install {package_name}")
                return False
        return True
    except Exception as e:
        logger.error(f"Error with package {package_name}: {str(e)}")
        return False

# Install required packages
ensure_package("mcp-server")
ensure_package("nltk")
ensure_package("textblob")
ensure_package("spacy")

# Import MCP after ensuring it's installed
from mcp.server import FastMCP

# Import text analysis packages
import nltk
from textblob import TextBlob
import re

# Download necessary NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.error(f"Error downloading NLTK resources: {str(e)}")

# Try to load spaCy model
try:
    ensure_package("spacy")
    import spacy
    # Check if English model is installed, if not, install the small model
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.info("Installing spaCy English model")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Error with spaCy: {str(e)}")
    nlp = None

# Create MCP server with a unique name
mcp = FastMCP("textanalyzer")

@mcp.tool()
async def analyze_text(
    text: str,
    operations: List[str] = ["basic", "sentiment", "entities"],
    max_keywords: int = 10
) -> Dict[str, Any]:
    '''
    Comprehensive text analysis tool that can perform multiple types of analysis.
    
    Args:
        text: The text to analyze
        operations: List of analysis types to perform. Options:
                    - "basic": Word count, character count, sentence count, etc.
                    - "sentiment": Sentiment analysis
                    - "entities": Named entity recognition
                    - "keywords": Extract key terms
                    - "readability": Readability scores
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        A dictionary with analysis results based on requested operations
    '''
    if not text:
        return {"error": "No text provided"}
    
    results = {}
    
    # Basic text statistics
    if "basic" in operations:
        words = text.split()
        sentences = nltk.sent_tokenize(text)
        
        results["basic"] = {
            "word_count": len(words),
            "character_count": len(text),
            "character_count_no_spaces": len(text.replace(" ", "")),
            "sentence_count": len(sentences),
            "average_word_length": sum(len(word) for word in words) / max(len(words), 1),
            "average_sentence_length": len(words) / max(len(sentences), 1),
        }
    
    # Sentiment analysis
    if "sentiment" in operations:
        try:
            blob = TextBlob(text)
            results["sentiment"] = {
                "polarity": blob.sentiment.polarity,  # -1 to 1 (negative to positive)
                "subjectivity": blob.sentiment.subjectivity,  # 0 to 1 (objective to subjective)
                "assessment": "positive" if blob.sentiment.polarity > 0.1 else 
                             "negative" if blob.sentiment.polarity < -0.1 else "neutral"
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            results["sentiment"] = {"error": str(e)}
    
    # Named entity recognition
    if "entities" in operations and nlp is not None:
        try:
            doc = nlp(text)
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                if ent.text not in entities[ent.label_]:
                    entities[ent.label_].append(ent.text)
            
            results["entities"] = entities
        except Exception as e:
            logger.error(f"Entity recognition error: {str(e)}")
            results["entities"] = {"error": str(e)}
    
    # Keyword extraction
    if "keywords" in operations:
        try:
            stopwords = set(nltk.corpus.stopwords.words('english'))
            words = [w.lower() for w in nltk.word_tokenize(text) 
                    if w.isalnum() and w.lower() not in stopwords]
            
            # Calculate frequency distribution
            fdist = nltk.FreqDist(words)
            keywords = []
            for word, freq in fdist.most_common(max_keywords):
                if len(word) > 2:  # Skip very short words
                    keywords.append({"word": word, "frequency": freq})
            
            results["keywords"] = keywords
        except Exception as e:
            logger.error(f"Keyword extraction error: {str(e)}")
            results["keywords"] = {"error": str(e)}
    
    # Readability metrics
    if "readability" in operations:
        try:
            word_count = len(text.split())
            sentence_count = max(len(nltk.sent_tokenize(text)), 1)
            syllable_pattern = re.compile(r'[aeiouy]+', re.IGNORECASE)
            syllable_count = 0
            
            for word in text.split():
                syllables = len(re.findall(syllable_pattern, word))
                syllable_count += max(1, syllables)  # Every word has at least one syllable
            
            # Calculate Flesch Reading Ease
            if sentence_count > 0 and word_count > 0:
                flesch_ease = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllable_count / word_count))
                
                # Calculate Flesch-Kincaid Grade Level
                flesch_grade = 0.39 * (word_count / sentence_count) + 11.8 * (syllable_count / word_count) - 15.59
                
                results["readability"] = {
                    "flesch_reading_ease": round(flesch_ease, 2),
                    "flesch_kincaid_grade": round(flesch_grade, 2),
                    "estimated_reading_time_minutes": round(word_count / 200, 2)  # Assuming 200 wpm reading speed
                }
            else:
                results["readability"] = {"error": "Text too short for readability analysis"}
        except Exception as e:
            logger.error(f"Readability analysis error: {str(e)}")
            results["readability"] = {"error": str(e)}
    
    return results

@mcp.tool()
async def compare_texts(text1: str, text2: str) -> Dict[str, Any]:
    '''
    Compare two texts and analyze similarities and differences.
    
    Args:
        text1: First text for comparison
        text2: Second text for comparison
        
    Returns:
        Dictionary with comparison metrics
    '''
    if not text1 or not text2:
        return {"error": "Both texts must be provided"}
    
    comparison = {}
    
    # Basic comparison stats
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    common_words = words1.intersection(words2)
    
    comparison["word_count"] = {
        "text1": len(text1.split()),
        "text2": len(text2.split())
    }
    
    comparison["unique_words"] = {
        "text1": len(words1),
        "text2": len(words2),
        "common": len(common_words)
    }
    
    # Calculate Jaccard similarity
    jaccard_similarity = len(common_words) / max(len(words1.union(words2)), 1)
    comparison["jaccard_similarity"] = round(jaccard_similarity, 4)
    
    # Calculate similarity based on TextBlob
    try:
        blob1 = TextBlob(text1)
        blob2 = TextBlob(text2)
        
        # Return sentiment difference
        comparison["sentiment_comparison"] = {
            "text1_polarity": blob1.sentiment.polarity,
            "text2_polarity": blob2.sentiment.polarity,
            "polarity_difference": abs(blob1.sentiment.polarity - blob2.sentiment.polarity),
            "subjectivity_difference": abs(blob1.sentiment.subjectivity - blob2.sentiment.subjectivity)
        }
    except Exception as e:
        logger.error(f"TextBlob comparison error: {str(e)}")
        comparison["sentiment_comparison"] = {"error": str(e)}
    
    return comparison

# Log to file, NOT to stdout
logger.info("Starting textanalyzer MCP tool")

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
