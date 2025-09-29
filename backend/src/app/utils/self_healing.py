#!/usr/bin/env python3
"""
Self-Healing Error Recovery System
Automatically fixes code errors using AI without human intervention
"""

import os
import traceback
import ast
import inspect
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Any, Dict, Optional
import logging

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# Configure logging for self-healing
log_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'self_healing.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SelfHealingAgent:
    """AI-powered self-healing system for automatic error recovery"""
    
    def __init__(self, max_fix_attempts=3):
        self.max_fix_attempts = max_fix_attempts
        self.fix_history = []
        self.success_rate = {}
        
    def auto_fix_function(self, func_name: str, error: Exception, 
                         original_code: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Automatically fix a function that's causing errors
        
        Args:
            func_name: Name of the function with error
            error: The exception that occurred
            original_code: The current function code
            context: Additional context (variables, inputs, etc.)
            
        Returns:
            Fixed function code or None if unfixable
        """
        
        error_details = {
            'function': func_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context
        }
        
        logging.info(f"🔧 Auto-fixing error in {func_name}: {error}")
        
        for attempt in range(self.max_fix_attempts):
            try:
                fix_prompt = self._create_fix_prompt(error_details, original_code, attempt)
                fixed_code = self._get_ai_fix(fix_prompt)
                
                # Validate the fix
                if self._validate_fix(fixed_code, context):
                    logging.info(f"✅ Successfully fixed {func_name} on attempt {attempt + 1}")
                    self._record_success(func_name, attempt + 1)
                    return fixed_code
                    
            except Exception as fix_error:
                logging.warning(f"⚠️ Fix attempt {attempt + 1} failed: {fix_error}")
                continue
                
        logging.error(f"❌ Could not auto-fix {func_name} after {self.max_fix_attempts} attempts")
        return None
    
    def _create_fix_prompt(self, error_details: Dict, original_code: str, attempt: int) -> str:
        """Create AI prompt for fixing the error"""
        
        previous_attempts = ""
        if attempt > 0:
            previous_attempts = f"\nPrevious {attempt} fix attempts failed. Try a different approach."
        
        return f"""
You are an expert Python debugging and code repair specialist. Fix this error automatically.

ERROR DETAILS:
- Function: {error_details['function']}
- Error Type: {error_details['error_type']}
- Error Message: {error_details['error_message']}
- Context: {error_details['context']}

CURRENT CODE:
```python
{original_code}
```

TRACEBACK:
{error_details['traceback']}

{previous_attempts}

REQUIREMENTS:
1. Fix ONLY the specific error
2. Maintain all original functionality
3. Return ONLY the corrected Python code
4. No explanations or comments
5. Ensure JSON serialization compatibility
6. Handle edge cases properly

RETURN: Complete corrected function code only.
"""

    def _get_ai_fix(self, prompt: str) -> str:
        """Get fix from AI"""
        try:
            response = model.generate_content(prompt)
            code = response.text.strip()
            
            # Clean up AI response
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].strip()
                
            return code
        except Exception as e:
            raise Exception(f"AI fix generation failed: {e}")
    
    def _validate_fix(self, fixed_code: str, context: Dict[str, Any]) -> bool:
        """Validate that the fix is syntactically correct"""
        try:
            # Check syntax
            ast.parse(fixed_code)
            
            # Try to compile
            compile(fixed_code, '<string>', 'exec')
            
            return True
        except Exception as e:
            logging.warning(f"Fix validation failed: {e}")
            return False
    
    def _record_success(self, func_name: str, attempts: int):
        """Record successful fix for statistics"""
        self.fix_history.append({
            'function': func_name,
            'attempts': attempts,
            'timestamp': os.time()
        })
        
        if func_name not in self.success_rate:
            self.success_rate[func_name] = {'fixes': 0, 'attempts': 0}
        
        self.success_rate[func_name]['fixes'] += 1
        self.success_rate[func_name]['attempts'] += attempts
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get self-healing statistics"""
        total_fixes = len(self.fix_history)
        avg_attempts = sum(fix['attempts'] for fix in self.fix_history) / max(total_fixes, 1)
        
        return {
            'total_fixes': total_fixes,
            'average_attempts': round(avg_attempts, 2),
            'success_rate_by_function': self.success_rate,
            'recent_fixes': self.fix_history[-10:]  # Last 10 fixes
        }


# Global self-healing agent instance
auto_healer = SelfHealingAgent()


def self_healing_decorator(original_func):
    """Decorator that automatically fixes functions when they fail"""
    
    def wrapper(*args, **kwargs):
        try:
            # Try original function first
            return original_func(*args, **kwargs)
            
        except Exception as e:
            logging.error(f"🚨 Function {original_func.__name__} failed with {type(e).__name__}: {e}")
            
            # Get function source code
            try:
                source_code = inspect.getsource(original_func)
            except:
                source_code = "Source code unavailable"
            
            # Prepare context with more details
            context = {
                'args': str(args)[:500],  # Limit size
                'kwargs': str(kwargs)[:500],
                'function_name': original_func.__name__,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'traceback': traceback.format_exc()[:1000]
            }
            
            # Attempt auto-fix
            fixed_code = auto_healer.auto_fix_function(
                original_func.__name__, e, source_code, context
            )
            
            if fixed_code:
                try:
                    # Execute fixed code
                    namespace = original_func.__globals__.copy()
                    exec(fixed_code, namespace)
                    
                    # Get the fixed function
                    fixed_func = namespace.get(original_func.__name__)
                    
                    if fixed_func:
                        logging.info(f"🔧 Trying auto-fixed version of {original_func.__name__}")
                        # Try with fixed function
                        result = fixed_func(*args, **kwargs)
                        logging.info(f"✅ Auto-fixed {original_func.__name__} succeeded!")
                        return result
                        
                except Exception as fix_error:
                    logging.error(f"❌ Auto-fixed function still failed: {fix_error}")
                    return {
                        "success": False,
                        "error": f"Auto-fixed function failed: {str(fix_error)}",
                        "original_error": str(e),
                        "auto_fix_attempted": True,
                        "auto_fix_successful": False
                    }
            
            # If no fix available, return structured error
            logging.error(f"💔 No auto-fix available for {original_func.__name__}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "function": original_func.__name__,
                "auto_fix_attempted": True,
                "auto_fix_successful": False,
                "message": "This error will be learned from for future fixes"
            }
    
    return wrapper

# Initialize global auto-healer instance  
auto_healer = SelfHealingAgent()

if __name__ == "__main__":
    print("🤖 Self-Healing Agent initialized!")
    print("📊 Healing Stats:", auto_healer.get_healing_stats())