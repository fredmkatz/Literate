# pip install zenrows
# from zenrows import ZenRowsClient

# ZEN_API = "fbb0c05297f1e31fde8df9b2210ae9493b1bd4c4"
# url = "https://claude.ai"

# response = client.get(url)

# print(response.text)


# pip install playwright
import asyncio
from playwright.async_api import async_playwright

ZEN_API = "fbb0c05297f1e31fde8df9b2210ae9493b1bd4c4"
url = "https://claude.ai"

# scraping browser connection URL
connection_url = f"wss://browser.zenrows.com?apikey={ZEN_API}"

async def scraper():
    async with async_playwright() as p:
        # connect to the scraping browser
        browser = await p.chromium.connect_over_cdp(connection_url)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await context.new_page()
        
        await page.goto('https://claude.ai')
        print(await page.title())

        chat_input_selectors = [
            ".is-editor-empty", 
            "textarea[placeholder*='How can I help you today?']",  # Common pattern
            "textarea[placeholder*='message']",  # Common pattern

            "textarea[placeholder*='message']",  # Common pattern
            "div[contenteditable='true']",       # Alternative
            "textarea",                          # Fallback
            "[data-testid='chat-input']"         # Possible test ID
        ]
        input_elment =  page.get_by_placeholder('How can I help you today?')
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


    await browser.close()

if __name__ == "__main__":
    asyncio.run(scraper())