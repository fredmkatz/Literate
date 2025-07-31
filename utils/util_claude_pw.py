from playwright.sync_api import sync_playwright, Page
import time
import json

class PlaywrightLDMAssistant:
    def __init__(self):
        self.page = None
        self.context = None
        self.playwright = None
        self.browser = None
        

    def start_browser(self, headless=False):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            slow_mo=1000,  # Slow down actions by 1 second (helpful for watching)
            devtools=True  # Opens dev tools automatically
        )
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
    def login(self, email: str, password: str):
        self.page.goto("https://claude.ai")
        # You'll need to inspect and find the actual selectors
        self.page.fill("input[type='email']", email)  # Example - not real
        self.page.fill("input[type='password']", password)
        self.page.click("button[type='submit']")  # Example
        
    def select_project(self, project_name: str):
        # Wait for projects to load
        self.page.wait_for_selector("project-selector")  # You'll find real selector
        # Click on project by name
        self.page.click(f"text={project_name}")
        
    def start_new_chat(self):
        self.page.click("new-chat-button")  # Find real selector
        
    def send_request(self, request_text: str) -> str:
        # Find the input area and send message
        self.page.fill("textarea", request_text)  # Find real selector
        self.page.click("send-button")  # Find real selector
        
        # Wait for response
        self.page.wait_for_selector("response-complete-indicator")  # Find real indicator
        p
        # Extract response - could be artifact or conversation text
        response = self.page.text_content("response-area")  # Find real selector
        return response


if __name__ == "__main__":
    claude = PlaywrightLDMAssistant()
    claude.start_browser(headless = False)
    claude.login("fmkatz@gmail.com", "Elfie-1943")
    claude.select_project("LDM API")