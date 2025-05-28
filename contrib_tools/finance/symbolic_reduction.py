import sys
import os
import logging
import sympy
from sympy import symbols, simplify, factor, expand, sympify, pretty
import numpy as np
from collections import Counter
import math

# Setup proper logging to file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "symbolic_reduction.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file)]
)
logger = logging.getLogger("symbolic_reduction")

__version__ = "0.1.1"
__updated__ = "2025-05-21"

# Function to safely serialize objects for logging
def safe_serialize(obj):
    # Safely serialize objects for logging, including handling non-serializable types.
    try:
        return json.dumps(obj, default=str)
    except (TypeError, OverflowError, ValueError) as e:
        return f"<Non-serializable value: {type(obj).__name__}>"

# Create MCP server with a unique name
logger.info("Initializing MCP server with name 'symbolic-reduction-server'")

# imports mcp-server with the correct import statement
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("symbolic-reduction-server")

@mcp.tool()
async def symbolic_reduction(operation: str, expression: str = None, data: list = None, 
                            text: str = None, reduction_level: int = 1, 
                            ctx: Context = None) -> dict:
    """
    Reduces complex information to its essential form using different techniques.
    
    Args:
        operation: Operation to perform (reduce_expression, find_patterns, semantic_reduce)
        expression: Mathematical expression to reduce (for reduce_expression)
        data: List of data points to analyze (for find_patterns)
        text: Text to reduce (for semantic_reduce)
        reduction_level: Level of reduction (1-3) for semantic_reduce
        ctx: The context object for logging and progress reporting
        
    Returns:
        Dictionary with reduction results and analysis
    """
    # Log input details using context
    if ctx:
        await ctx.info(f"Symbolic reduction called with operation: {operation}")
    else:
        logger.info(f"Symbolic reduction called with operation: {operation}")
    
    try:
        if operation == "reduce_expression" and expression:
            # Report progress
            if ctx:
                await ctx.report_progress(progress=0, total=100)
                
            result = await reduce_expression(expression, ctx)
            
            # Final progress report
            if ctx:
                await ctx.report_progress(progress=100, total=100)
                
            return result
        elif operation == "find_patterns" and data:
            # Report progress
            if ctx:
                await ctx.report_progress(progress=0, total=100)
                
            result = await find_patterns(data, ctx)
            
            # Final progress report
            if ctx:
                await ctx.report_progress(progress=100, total=100)
                
            return result
        elif operation == "semantic_reduce" and text:
            # Report progress
            if ctx:
                await ctx.report_progress(progress=0, total=100)
                
            result = await semantic_reduce(text, reduction_level, ctx)
            
            # Final progress report
            if ctx:
                await ctx.report_progress(progress=100, total=100)
                
            return result
        else:
            if ctx:
                await ctx.warning(f"Invalid operation or missing required parameters for {operation}")
                
            return {
                "status": "error",
                "message": f"Invalid operation or missing required parameters for {operation}"
            }
    except Exception as e:
        if ctx:
            await ctx.error(f"Error in symbolic_reduction: {str(e)}")
        else:
            logger.error(f"Error in symbolic_reduction: {str(e)}")
            
        return {
            "status": "error",
            "message": str(e)
        }

async def reduce_expression(expression, ctx=None):
    """Reduces a mathematical expression to its simplest form"""
    try:
        if ctx:
            await ctx.info(f"Reducing expression: {expression}")
            await ctx.report_progress(progress=10, total=100)
            
        # Parse the expression with sympy
        expr = sympify(expression)
        
        if ctx:
            await ctx.debug("Expression parsed successfully")
            await ctx.report_progress(progress=30, total=100)
        
        # Perform various reductions
        simplified = simplify(expr)
        
        if ctx:
            await ctx.report_progress(progress=50, total=100)
            
        factored = factor(simplified)
        
        if ctx:
            await ctx.report_progress(progress=70, total=100)
            
        expanded = expand(simplified)
        
        if ctx:
            await ctx.report_progress(progress=80, total=100)
        
        # Determine which form is most reduced by string length
        forms = {
            "simplified": simplified,
            "factored": factored, 
            "expanded": expanded
        }
        
        form_lengths = {name: len(str(form)) for name, form in forms.items()}
        most_reduced_form = min(form_lengths, key=form_lengths.get)
        
        if ctx:
            await ctx.report_progress(progress=90, total=100)
            await ctx.info(f"Reduction complete. Most reduced form: {most_reduced_form}")
        
        return {
            "status": "success",
            "original": str(expr),
            "simplified": str(simplified),
            "factored": str(factored),
            "expanded": str(expanded),
            "most_reduced": str(forms[most_reduced_form]),
            "reduction_form": most_reduced_form,
            "pretty_print": pretty(forms[most_reduced_form]),
            "reduction_percentage": round((1 - form_lengths[most_reduced_form]/len(expression)) * 100, 2)
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"Error in reduce_expression: {str(e)}")
        else:
            logger.error(f"Error in reduce_expression: {str(e)}")
            
        return {
            "status": "error",
            "message": str(e),
            "original": expression
        }

async def find_patterns(data, ctx=None):
    """Analyzes data to find patterns and reductions"""
    results = {"status": "success", "original_data": data}
    
    try:
        if ctx:
            await ctx.info(f"Finding patterns in data with {len(data)} elements")
            await ctx.report_progress(progress=10, total=100)
            
        # Convert all elements to the same type if possible
        try:
            numeric_data = [float(x) for x in data]
            is_numeric = True
            
            if ctx:
                await ctx.debug("Data is numeric, performing numerical pattern analysis")
                
        except:
            is_numeric = False
            
            if ctx:
                await ctx.debug("Data is not numeric, skipping numerical pattern analysis")
                
        if ctx:
            await ctx.report_progress(progress=30, total=100)
            
        # Pattern analysis for numeric data
        if is_numeric:
            # Check for arithmetic sequence
            differences = [numeric_data[i+1] - numeric_data[i] for i in range(len(numeric_data)-1)]
            if len(set(round(d, 10) for d in differences)) == 1:
                results["pattern_type"] = "arithmetic_sequence"
                results["common_difference"] = differences[0]
                results["formula"] = f"a(n) = {numeric_data[0]} + (n-1)*{differences[0]}"
                results["next_value"] = numeric_data[0] + len(numeric_data) * differences[0]
                
                if ctx:
                    await ctx.info(f"Arithmetic sequence detected with common difference {differences[0]}")
            
            # Check for geometric sequence
            if all(x != 0 for x in numeric_data):
                ratios = [numeric_data[i+1] / numeric_data[i] for i in range(len(numeric_data)-1)]
                if len(set(round(r, 10) for r in ratios)) == 1:
                    results["pattern_type"] = "geometric_sequence"
                    results["common_ratio"] = ratios[0]
                    results["formula"] = f"a(n) = {numeric_data[0]} * {ratios[0]}^(n-1)"
                    results["next_value"] = numeric_data[0] * (ratios[0] ** len(numeric_data))
                    
                    if ctx:
                        await ctx.info(f"Geometric sequence detected with common ratio {ratios[0]}")
            
            if ctx:
                await ctx.report_progress(progress=60, total=100)
        
        # Pattern analysis for any data type
        # Find most common elements
        counter = Counter(data)
        results["frequency_analysis"] = dict(counter.most_common())
        
        if ctx:
            await ctx.report_progress(progress=70, total=100)
        
        # Calculate information entropy
        total = len(data)
        probabilities = [count/total for count in counter.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities)
        results["entropy"] = entropy
        
        if ctx:
            await ctx.report_progress(progress=80, total=100)
        
        # Calculate compression potential
        max_entropy = math.log2(len(counter))
        if max_entropy > 0:
            results["redundancy"] = 1 - (entropy / max_entropy)
            results["compression_potential"] = f"{results['redundancy'] * 100:.2f}%"
            
            if ctx:
                await ctx.info(f"Analysis complete. Entropy: {entropy:.2f}, Compression potential: {results['compression_potential']}")
        
        if ctx:
            await ctx.report_progress(progress=90, total=100)
        
        return results
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Error in find_patterns: {str(e)}")
        else:
            logger.error(f"Error in find_patterns: {str(e)}")
            
        return {
            "status": "error",
            "message": str(e),
            "original_data": data
        }

async def semantic_reduce(text, reduction_level=1, ctx=None):
    """Reduces text to its essential components"""
    try:
        if ctx:
            await ctx.info(f"Semantic reduction with level {reduction_level}")
            await ctx.report_progress(progress=10, total=100)
            
        original_length = len(text)
        words = text.split()
        
        if ctx:
            await ctx.debug(f"Text contains {len(words)} words, {original_length} characters")
            await ctx.report_progress(progress=30, total=100)
        
        # Calculate word frequency
        word_freq = Counter(word.lower() for word in words)
        
        if ctx:
            await ctx.report_progress(progress=50, total=100)
        
        # Define filler words for different reduction levels
        filler_words = {
            1: {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were'},
            2: {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                'that', 'this', 'these', 'those', 'to', 'for', 'in', 'on', 'at', 'by'},
            3: {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                'that', 'this', 'these', 'those', 'to', 'for', 'in', 'on', 'at', 'by',
                'with', 'from', 'as', 'of', 'about', 'like', 'than', 'after', 'before'}
        }
        
        if ctx:
            await ctx.report_progress(progress=70, total=100)
        
        # Apply the reduction
        if 1 <= reduction_level <= 3:
            filtered_words = [word for word in words if word.lower() not in filler_words[reduction_level]]
            reduced_text = ' '.join(filtered_words)
        else:
            reduced_text = text
            
        if ctx:
            await ctx.report_progress(progress=80, total=100)
            
        # Calculate reduction statistics
        reduced_length = len(reduced_text)
        reduction_percentage = ((original_length - reduced_length) / original_length) * 100 if original_length > 0 else 0
        
        # Identify key terms (most frequent meaningful words)
        common_words = word_freq.most_common(5)
        
        if ctx:
            await ctx.info(f"Reduction complete. Original length: {original_length}, Reduced length: {reduced_length}")
            await ctx.report_progress(progress=90, total=100)
        
        return {
            "status": "success",
            "original_text": text,
            "reduced_text": reduced_text,
            "original_length": original_length,
            "reduced_length": reduced_length,
            "reduction_percentage": f"{reduction_percentage:.2f}%",
            "reduction_level": reduction_level,
            "key_terms": common_words
        }
    
    except Exception as e:
        if ctx:
            await ctx.error(f"Error in semantic_reduce: {str(e)}")
        else:
            logger.error(f"Error in semantic_reduce: {str(e)}")
            
        return {
            "status": "error",
            "message": str(e),
            "original_text": text
        }

# Log application startup
logger.info(f"Starting Symbolic Reduction MCP tool version {__version__}")
logger.info(f"Logging to: {log_file}")
logger.info(f"Python version: {sys.version}")

# Start the MCP server
if __name__ == "__main__":
    try:
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Failed to start: {str(e)}", exc_info=True)
        sys.exit(1)
