import logging
import sys
import functools
import inspect
from typing import Optional, Callable, Any, Union, Dict
from contextlib import contextmanager

# Default format for log messages
DEFAULT_FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s()] %(message)s"

# Configure basic logging
logging.basicConfig(stream=sys.stdout, format=DEFAULT_FORMAT, level=logging.INFO)

class EnhancedLogger(logging.Logger):
    """
    Enhanced logger with improved f-string support, stack level management,
    and level management.
    """
    
    def __init__(self, name: str, level: int = logging.NOTSET):
        """Initialize the enhanced logger."""
        super().__init__(name, level)
        self._level_stack = []
        self._transparent_depth = 0
    
    def setLevel(self, level: int) -> int:
        """
        Set the logging level and return the previous level.
        
        Args:
            level: New logging level
            
        Returns:
            Previous logging level
        """
        old_level = self.level
        super().setLevel(level)
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, f"Log level changed from {old_level} to {level}", (), 
                     stacklevel=2)
        return old_level
    
    @contextmanager
    def temp_level(self, level: int):
        """
        Temporarily change the logging level within a context.
        
        Args:
            level: The logging level to use within the context
            
        Usage:
            with logger.temp_level(logging.DEBUG):
                logger.debug("This will be logged at DEBUG level")
        """
        old_level = self.setLevel(level)
        try:
            yield
        finally:
            self.setLevel(old_level)
    
    @contextmanager
    def transparent(self, additional_depth=0):
        """
        Context manager to make a function transparent in the logging stack.
        
        Any log calls within this context will show as coming from the caller.
        
        Args:
            additional_depth: How many additional frames to skip (default: 1)
        """
        self._transparent_depth += additional_depth
        try:
            yield
        finally:
            self._transparent_depth -= additional_depth
    
    def push_level(self, level: int):
        """
        Push current level onto stack and set a new level.
        
        Args:
            level: New logging level to set
        """
        self._level_stack.append(self.level)
        self.setLevel(level)
    
    def pop_level(self):
        """
        Restore the previous logging level from the stack.
        
        Returns:
            The current level after popping
        """
        if self._level_stack:
            level = self._level_stack.pop()
            self.setLevel(level)
            return level
        return self.level
    
    def debug(self, msg: str, *args, **kwargs):
        """
        Log a message with severity 'DEBUG'.
        
        This is enhanced to better handle f-strings and stack levels.
        
        Args:
            msg: The message to log
            *args: Arguments to use for string formatting (not needed for f-strings)
            **kwargs: Additional logging parameters
        """
        stacklevel = kwargs.pop('stacklevel', 1) + 1 + self._transparent_depth
        if self.isEnabledFor(logging.DEBUG):
            self._log(logging.DEBUG, indented(msg), args, stacklevel=stacklevel, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log a message with severity 'INFO'."""
        stacklevel = kwargs.pop('stacklevel', 1) + 1 + self._transparent_depth
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, indented(msg), args, stacklevel=stacklevel, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log a message with severity 'WARNING'."""
        stacklevel = kwargs.pop('stacklevel', 1) + 1 + self._transparent_depth
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, indented(msg), args, stacklevel=stacklevel, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log a message with severity 'ERROR'."""
        stacklevel = kwargs.pop('stacklevel', 1) + 1 + self._transparent_depth
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, indented(msg), args, stacklevel=stacklevel, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log a message with severity 'CRITICAL'."""
        stacklevel = kwargs.pop('stacklevel', 1) + 1 + self._transparent_depth
        if self.isEnabledFor(logging.CRITICAL):
            self._log(logging.CRITICAL, indented(msg), args, stacklevel=stacklevel, **kwargs)
    
    # Convenience methods for f-string use
    def debugf(self, msg: str, stacklevel: int = 1, **kwargs):
        """Debug log with f-string support."""
        self.debug(msg, stacklevel=stacklevel+1, **kwargs)
    
    def infof(self, msg: str, stacklevel: int = 1, **kwargs):
        """Info log with f-string support."""
        self.info(msg, stacklevel=stacklevel+1, **kwargs)
    
    def warningf(self, msg: str, stacklevel: int = 1, **kwargs):
        """Warning log with f-string support."""
        self.warning(msg, stacklevel=stacklevel+1, **kwargs)
    
    def errorf(self, msg: str, stacklevel: int = 1, **kwargs):
        """Error log with f-string support."""
        self.error(msg, stacklevel=stacklevel+1, **kwargs)
    
    def criticalf(self, msg: str, stacklevel: int = 1, **kwargs):
        """Critical log with f-string support."""
        self.critical(msg, stacklevel=stacklevel+1, **kwargs)

def indented(msg: str) -> str:
    """Indent the message for better readability."""
    initial_depth =10
    
    return ". " * (get_stack_depth() - initial_depth) + msg
    # return ". " * (get_stack_depth() ) + msg

def get_stack_depth():
  """Returns the current depth of the call stack."""
  return len(inspect.stack())

def transparent(func=None, *, depth=1):
    """
    Decorator to make a function transparent in logs.
    
    This decorator makes the function and all functions called within it
    appear transparent in logs (they'll show the original caller).
    
    Args:
        func: The function to decorate
        depth: How many additional stack frames to skip
        
    Returns:
        Decorated function
    
    Example:
        @transparent
        def helper_function():
            logger.info("This will look like it came from the caller")
            nested_helper()  # This will also look like it came from the caller
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Save the original depth
            current_depth = flogger._transparent_depth
            
            # Increase depth to make this function and its wrapper transparent
            # Add 1 for this wrapper function
            flogger._transparent_depth = current_depth + depth + 1
            
            try:
                # The actual function call
                return func(*args, **kwargs)
            finally:
                # Always restore original depth
                flogger._transparent_depth = current_depth
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


# Initialize the global logger
logging.setLoggerClass(EnhancedLogger)
flogger = logging.getLogger("flogger")
flogger.setLevel(logging.INFO)

import functools
    
def trace_decorator(func):
    @transparent(depth=1)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log the function call with its arguments
        flogger.infof(f"< {func.__name__} of {args} {kwargs}")
        result = func(*args, **kwargs)
        flogger.infof(f"> {func.__name__} returned {result}")
        return result
    return wrapper

def trace_method(func):
    @transparent(depth=1)
    @functools.wraps(func)
    @transparent  # Skip the wrapper and the method itself
    def wrapper(*args, **kwargs):
        # Log the function call with its arguments
        flogger.infof(f"< {func.__name__} of {args[1:]} {kwargs}")
        result = func(*args, **kwargs)
        flogger.infof(f"> {result} - from {func.__name__}")
        return result
    return wrapper
    
    # @trace_decorator
    # def add(x, y):
    #     return x + y
    
    # add(2, 3)
# # Example usage
# if __name__ == "__main__":
#     def test_function():
#         value = 42
#         flogger.debugf(f"Debug message with value: {value}")
#         flogger.infof(f"Info message with value: {value}")
        
#         # Testing level management
#         with flogger.temp_level(logging.DEBUG):
#             flogger.debug("This debug message will be shown")
        
#         flogger.debug("This debug message won't be shown")
        
#         # Stack manipulation
#         flogger.push_level(logging.DEBUG)
#         flogger.debug("Debug after push")
#         flogger.pop_level()
#         flogger.debug("Debug after pop")
    
#     @transparent
#     def helper_function():
#         # This will show the caller of helper_function in the log
#         flogger.info("Inside helper but log shows caller")
#         nested_helper()

#     @transparent
#     def nested_helper():
#         flogger.info("Inside nested_helper but should show caller")

#     def caller_function():
#         helper_function()
#         flogger.info("Inside caller, but outside helper")
            
#     test_function()
#     caller_function()