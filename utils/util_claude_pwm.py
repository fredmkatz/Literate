#!/usr/bin/env python3
"""
Hybrid Playwright Assistant - Manual navigation, automated request/response
"""

from playwright.sync_api import sync_playwright, Page
# from playwright_stealth import stealth_sync

import time
import json
import re
from typing import Optional

class HybridPlaywrightAssistant:
    def __init__(self):
        self.page = None
        self.context = None
        self.playwright = None

    def connect_to_existing_browser(self, port: int = 9222):
        """Connect to a manually opened browser"""
        print("Please:")
        print("1. Close any existing Chrome instances")
        print("2. Start Chrome with remote debugging:")
        print(f"   chrome --remote-debugging-port={port} --user-data-dir=/tmp/chrome-debug")
        print("3. Navigate to claude.ai, login, and go to your Project")
        input("Press Enter when ready...")
        
        # Connect to the existing browser
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{port}")
        
        # Get the existing page/tab
        contexts = self.browser.contexts
        if contexts:
            self.context = contexts[0]  # Use first context
            pages = self.context.pages
            if pages:
                self.page = pages[0]  # Use first page
        
        if not self.page:
            print("Could not connect to existing page")
            return False
            
        print(f"Connected! Current URL: {self.page.url}")
        return True
    
    # Then use browser automation just for the request/response part
    # through clipboard or other methods

    def start_and_wait_for_manual_setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        # # Apply stealth techniques
        # stealth_sync(self.page)

        
        # Go to Claude
        self.page.goto("https://claude.ai")
        
        print("\n" + "="*60)
        print("MANUAL SETUP REQUIRED")
        print("="*60)
        print("Please:")
        print("1. Login to Claude if needed")
        print("2. Navigate to your LDM Project")
        print("3. Start a new conversation")
        print("4. Make sure you're ready to send messages")
        print("="*60)
        
        input("Press Enter when you're ready for automation to begin...")
        print("Great! Now I can automate the request/response cycle.")
        
    def make_request(self, request_text: str, timeout: int = 60) -> Optional[str]:
        """Send request and extract response"""
        try:
            print(f"Sending request: {request_text[:100]}...")
            
            # Find and fill the chat input
            # You'll need to inspect Claude's interface for the right selector
            chat_input_selectors = [
                ".is-editor-empty", 
                "textarea[placeholder*='How can I help you today?']",  # Common pattern
                "textarea[placeholder*='message']",  # Common pattern

                "textarea[placeholder*='message']",  # Common pattern
                "div[contenteditable='true']",       # Alternative
                "textarea",                          # Fallback
                "[data-testid='chat-input']"         # Possible test ID
            ]
            input_elment = self.page.get_by_placeholder('How can I help you today?')
            if input_element:
                print("Found by placeholder")
            else:
                input_element = None
                for selector in chat_input_selectors:
                    try:
                        input_element = self.page.wait_for_selector(selector, timeout=2000)
                        break
                    except:
                        continue
                    
            if not input_element:
                print("Could not find chat input. Please check the selector.")
                return None
            
            # Clear any existing text and type the request
            input_element.click()
            self.page.keyboard.press("Control+a")  # Select all
            self.page.keyboard.type(request_text)
            
            # Send the message (usually Enter or a send button)
            send_button_selectors = [
                "button[aria-label*='Send']",
                "button[type='submit']",
                "[data-testid='send-button']"
            ]
            
            # Try Enter key first
            self.page.keyboard.press("Enter")
            
            # Wait for response to appear and complete
            print("Waiting for Claude's response...")
            
            # Look for indicators that Claude is done responding
            completion_indicators = [
                "text=Copy",                    # Copy button appears when done
                "[data-testid='copy-button']", # Alternative copy button
                "button:has-text('Copy')",     # Button containing "Copy"
            ]
            
            # Wait for response completion (with timeout)
            response_ready = False
            for indicator in completion_indicators:
                try:
                    self.page.wait_for_selector(indicator, timeout=timeout*1000)
                    response_ready = True
                    break
                except:
                    continue
            
            if not response_ready:
                print("Timeout waiting for response completion")
                return None
            
            print("Response completed. Extracting text...")
            
            # Extract the response text
            # This is the trickiest part - you'll need to find the right selector
            response_selectors = [
                ".message:last-child .message-content",  # Common pattern
                "[data-testid='message-content']:last-child",
                ".response-content:last-child",
                ".conversation-turn:last-child .content"
            ]
            
            response_text = None
            for selector in response_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        response_text = element.inner_text()
                        break
                except:
                    continue
            
            if not response_text:
                print("Could not extract response text. You may need to copy manually.")
                print("Response should be visible in the browser window.")
                manual_response = input("Please copy and paste the response here:\n")
                return manual_response
            
            return response_text
            
        except Exception as e:
            print(f"Error during request: {e}")
            return None
    
    def extract_json_from_response(self, response_text: str) -> Optional[dict]:
        """Extract JSON from Claude's response"""
        if not response_text:
            return None
            
        try:
            # Look for JSON in code blocks first
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            if matches:
                return json.loads(matches[0])
            
            # Look for standalone JSON
            json_pattern = r'(\{.*\})'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            
            for match in matches:
                try:
                    return json.loads(match)
                except:
                    continue
                    
            print("Could not find valid JSON in response")
            return None
            
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return None
    
    def make_json_request(self, request_text: str) -> Optional[dict]:
        """Send request and return parsed JSON response"""
        response_text = self.make_request(request_text)
        if response_text:
            return self.extract_json_from_response(response_text)
        return None
    
    def close(self):
        """Clean up browser resources"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

# Usage example
def main():
    assistant = HybridPlaywrightAssistant()
    
    try:
        # Start browser and wait for manual setup
        # assistant.start_and_wait_for_manual_setup()
        assistant.connect_to_existing_browser()
        print("connected")
        # Now you can make automated requests
        requests = [
            "Review the Component class in the model doc. Fix all one-liners to be proper noun phrases. Return JSON with changes as specified in the instructions.",
            "Add missing Python expressions for all constraints and derivations in the AnnotationType class. Return JSON with changes.",
            "Complete review of the Subject class documentation. Return JSON with improvements."
        ]
        
        results = []
        for i, request in enumerate(requests):
            print(f"\n--- Request {i+1} ---")
            
            # Make the request
            result = assistant.make_json_request(request)
            
            if result:
                print(f"Success! Got {len(result.get('changes', []))} changes")
                results.append(result)
                
                # Save result
                with open(f"result_{i+1}.json", "w") as f:
                    json.dump(result, f, indent=2)
            else:
                print("Request failed or returned invalid JSON")
            
            # Pause between requests
            if i < len(requests) - 1:
                input("Press Enter for next request...")
        
        print(f"\nCompleted {len(results)} successful requests")
        
    finally:
        assistant.close()

if __name__ == "__main__":
    main()