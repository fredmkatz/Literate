import json
from typing import Dict, Any, Optional, Union
from anthropic import APIError, APIConnectionError, RateLimitError, AuthenticationError

def parse_claude_response_with_errors(claude_response) -> Dict[str, Any]:
    """
    Parse Claude API response including success and error cases.
    
    Args:
        claude_response: The Message object returned by the Claude API (success case)
        
    Returns:
        dict: Complete parsed response with metadata and content
    """
    try:
        # Extract metadata from successful response
        response_data = {
            'success': True,
            'id': claude_response.id,
            'model': claude_response.model,
            'role': claude_response.role,
            'stop_reason': claude_response.stop_reason,
            'stop_sequence': claude_response.stop_sequence,
            'type': claude_response.type,
            
            # Usage information
            'usage': {
                'input_tokens': claude_response.usage.input_tokens,
                'output_tokens': claude_response.usage.output_tokens,
                'cache_creation_input_tokens': claude_response.usage.cache_creation_input_tokens,
                'cache_read_input_tokens': claude_response.usage.cache_read_input_tokens,
                'service_tier': claude_response.usage.service_tier,
                'total_tokens': claude_response.usage.input_tokens + claude_response.usage.output_tokens
            },
            
            # Content blocks
            'content_blocks': [],
            'error': None
        }
        
        # Process each content block
        for block in claude_response.content:
            block_data = {
                'type': block.type,
                'citations': getattr(block, 'citations', None)
            }
            
            # Try to parse the text as JSON, fall back to raw text
            if hasattr(block, 'text'):
                try:
                    # Attempt to parse as JSON
                    parsed_json = json.loads(block.text)
                    block_data['parsed_json'] = parsed_json
                    block_data['raw_text'] = block.text
                    block_data['is_json'] = True
                except json.JSONDecodeError:
                    # Not JSON, store as raw text
                    block_data['text'] = block.text
                    block_data['is_json'] = False
            
            response_data['content_blocks'].append(block_data)
        
        return response_data
    
    except AttributeError as e:
        return {
            'success': False,
            'error': {
                'type': 'parsing_error',
                'message': f"Invalid Claude response structure: {e}",
                'details': str(e)
            }
        }

def handle_claude_api_call(client, **kwargs) -> Dict[str, Any]:
    """
    Make a Claude API call with comprehensive error handling.
    
    Args:
        client: Anthropic client instance
        **kwargs: Arguments to pass to client.messages.create()
        
    Returns:
        dict: Parsed response with success/error information
    """
    try:
        # Make the API call
        response = client.messages.create(**kwargs)
        
        # Parse successful response
        return parse_claude_response_with_errors(response)
        
    except AuthenticationError as e:
        return {
            'success': False,
            'error': {
                'type': 'authentication_error',
                'status_code': e.status_code,
                'message': 'Invalid API key or authentication failed',
                'details': str(e)
            }
        }
    
    except RateLimitError as e:
        return {
            'success': False,
            'error': {
                'type': 'rate_limit_error',
                'status_code': e.status_code,
                'message': 'Rate limit exceeded',
                'details': str(e),
                'retry_after': getattr(e, 'retry_after', None)
            }
        }
    
    except APIConnectionError as e:
        return {
            'success': False,
            'error': {
                'type': 'connection_error',
                'message': 'Failed to connect to Claude API',
                'details': str(e)
            }
        }
    
    except APIError as e:
        return {
            'success': False,
            'error': {
                'type': 'api_error',
                'status_code': getattr(e, 'status_code', None),
                'message': 'Claude API returned an error',
                'details': str(e),
                'error_code': getattr(e, 'code', None)
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': {
                'type': 'unexpected_error',
                'message': 'An unexpected error occurred',
                'details': str(e)
            }
        }

def parse_error_response(error_dict: Dict[str, Any]) -> str:
    """
    Generate human-readable error message from error response.
    
    Args:
        error_dict: Error dictionary from failed API call
        
    Returns:
        str: Formatted error message
    """
    if not error_dict.get('error'):
        return "Unknown error occurred"
    
    error = error_dict['error']
    error_type = error.get('type', 'unknown')
    message = error.get('message', 'No message provided')
    status_code = error.get('status_code')
    
    if status_code:
        return f"{error_type.replace('_', ' ').title()} ({status_code}): {message}"
    else:
        return f"{error_type.replace('_', ' ').title()}: {message}"

# Example usage
def example_usage_with_errors():
    """
    Demonstrate comprehensive error handling with Claude API.
    """
    from anthropic import Anthropic
    
    # Initialize client
    # client = Anthropic(api_key="your-api-key")
    
    # Example API call with error handling
    # result = handle_claude_api_call(
    #     client,
    #     model="claude-3-5-sonnet-20241022",
    #     max_tokens=1000,
    #     messages=[{"role": "user", "content": "Hello!"}]
    # )
    
    # Example successful response structure
    success_example = {
        'success': True,
        'id': 'msg_01BXUs9xVy1LKpYtiMzDntXa',
        'model': 'claude-3-5-sonnet-20241022',
        'role': 'assistant',
        'stop_reason': 'end_turn',
        'usage': {
            'input_tokens': 30204,
            'output_tokens': 693,
            'total_tokens': 30897
        },
        'content_blocks': [
            {
                'type': 'text',
                'is_json': True,
                'parsed_json': {
                    'response_type': 'changes',
                    'changes': []
                }
            }
        ],
        'error': None
    }
    
    # Example error response structure
    error_example = {
        'success': False,
        'error': {
            'type': 'rate_limit_error',
            'status_code': 429,
            'message': 'Rate limit exceeded',
            'details': 'Request was throttled. Expected available in 60 seconds.',
            'retry_after': 60
        }
    }
    
    # How to handle the response
    def process_response(result):
        if result['success']:
            print(f"✅ Success! Model: {result['model']}")
            print(f"Tokens used: {result['usage']['total_tokens']}")
            
            # Check if content is JSON
            for block in result['content_blocks']:
                if block.get('is_json'):
                    json_data = block['parsed_json']
                    print(f"JSON Response Type: {json_data.get('response_type')}")
                else:
                    print(f"Text Response: {block.get('text', '')[:100]}...")
        else:
            error_msg = parse_error_response(result)
            print(f"❌ Error: {error_msg}")
            
            # Handle specific error types
            if result['error']['type'] == 'rate_limit_error':
                retry_after = result['error'].get('retry_after', 60)
                print(f"Retry after {retry_after} seconds")
            elif result['error']['type'] == 'authentication_error':
                print("Check your API key")
    
    print("Example successful response:")
    process_response(success_example)
    
    print("\nExample error response:")
    process_response(error_example)

# Quick helper for existing code migration
def safe_parse_claude_response(claude_response) -> tuple[Optional[Dict], Optional[str]]:
    """
    Simple wrapper that returns (json_data, error_message).
    
    Returns:
        tuple: (parsed_json_or_None, error_message_or_None)
    """
    try:
        result = parse_claude_response_with_errors(claude_response)
        if result['success']:
            # Try to get JSON from first content block
            for block in result['content_blocks']:
                if block.get('is_json'):
                    return block['parsed_json'], None
            return None, "No JSON content found in response"
        else:
            return None, parse_error_response(result)
    except Exception as e:
        return None, f"Parsing failed: {str(e)}"

if __name__ == "__main__":
    example_usage_with_errors()