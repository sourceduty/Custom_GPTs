import requests
import re
import sys
import webbrowser
import unicodedata
from colorama import init, Fore


class ReadMeViewer:
    def __init__(self):
        init(autoreset=True)
        
        self.categories_of_interest = [
            "ChatGPT", "Python", "Data & Programming", "Research, Math & Education",
            "Security & Military", "Science, Mechanical & Electronics", "Image & GIF",
            "Video", "Money", "Shopping", "Chatting", "Writing & Reading",
            "Government & Law", "Food & Farming", "Audio & Music",
            "Social Media & Social Tools", "Business & Productivity",
            "Art, Images & Design", "Travel, Hunting & Lifestyle", "Fun & Games",
            "General"  # Add a general category for unclassified links
        ]
        
        self.links = {cat: [] for cat in self.categories_of_interest}  # Initialize with categories
        self.expected_link_count = 0  
        self.total_links = 0  
        
        self.normalized_categories = {
            self.normalize_text(cat): cat for cat in self.categories_of_interest
        }

    def normalize_text(self, text):
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if c.isalnum()).lower()
        return text

    def fetch_readme(self, url):
        """Fetch the raw README.md content from the GitHub repository."""
        raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        response = requests.get(raw_url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"{Fore.RED}Error fetching README: {response.status_code}")
            return None

    def extract_expected_link_count(self, content):
        lines = content.splitlines()
        if len(lines) >= 5:
            line_5 = lines[4]
            match = re.search(r'`(\d+)`', line_5)  
            if match:
                self.expected_link_count = int(match.group(1))  
                print(f"{Fore.BLUE}Expected link count extracted: {self.expected_link_count}")
            else:
                print(f"{Fore.YELLOW}Warning: Expected link count not found on line 5.")
        else:
            print(f"{Fore.YELLOW}Warning: README content is less than 5 lines.")

    def extract_links(self, content):
        # Use regex to find Markdown-style links
        markdown_links = re.findall(r'\[(.*?)\]\((http[s]?://[^\s]+)\)', content)
        
        # Add the links to the 'General' category
        for link_text, link_url in markdown_links:
            self.links['General'].append((link_text, link_url))
        
        self.total_links = len(markdown_links)  # Calculate total links

    def display_statistics(self):
        print(f"{Fore.BLUE}Total number of links counted: {self.total_links}")  
        print(f"{Fore.BLUE}Expected total number of links: {self.expected_link_count}")
        if self.total_links != self.expected_link_count:
            print(f"{Fore.YELLOW}Warning: The counted links do not match the expected count.")
        else:
            print(f"{Fore.GREEN}Link counts match!")

    def display_categories(self):
        print(f"{Fore.GREEN}Main Categories:")
        print(f"{Fore.YELLOW}{'-' * 40}")  
        categories = list(self.links.keys())
        for i, category in enumerate(categories, start=1):
            print(f"{Fore.GREEN}{i}. {category} ({len(self.links[category])} links)")

    def display_links(self, category):
        links = self.links[category]
        print(f"\n{Fore.GREEN}Links in '{category}' (Count: {len(links)}):")
        print(f"{Fore.YELLOW}{'-' * 40}")  
        if links:
            for i, (link_text, link_url) in enumerate(links, start=1):
                print(f"{Fore.GREEN}{i}. {link_text} (URL: {link_url})")
        else:
            print(f"{Fore.YELLOW}No links available in this category.")

        self.open_link(links)

    def open_link(self, links):
        while True:
            link_choice = input(
                f"\n{Fore.GREEN}Enter the number of the link to open "
                f"(or 'back' to return to categories): ").strip()
            if link_choice.lower() in ('back', 'b'):
                break
            elif link_choice.lower() in ('exit', 'quit', 'q'):
                print(f"{Fore.GREEN}Exiting the program.")
                sys.exit(0)
            try:
                link_index = int(link_choice) - 1
                if 0 <= link_index < len(links):
                    _, link_url = links[link_index]
                    webbrowser.open(link_url)
                    print(f"{Fore.GREEN}Opening link: {link_url}")
                else:
                    print(f"{Fore.RED}Invalid selection. Please try again.")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.")

    def display_help_menu(self):
        help_text = (
            f"{Fore.BLUE}Help Menu:\n"
            f"{'-' * 40}\n"
            "1. Select a category by entering its number.\n"
            "2. After selecting a category, choose a link number to open it in your web browser.\n"
            "3. Use 'back' to return to the category selection menu.\n"
            "4. Type 'exit' at any time to close the program.\n"
            "5. You can type 'help' at any time to view this menu again.\n"
            f"{'-' * 40}"
        )
        print(help_text)

    def select_category(self):
        while True:
            self.display_categories()
            choice = input(
                f"{Fore.GREEN}\nSelect a category by number "
                f"(or 'exit' to quit, 'help' for help): ").strip()
            if choice.lower() in ('exit', 'quit', 'q'):
                print(f"{Fore.GREEN}Exiting the program.")
                sys.exit(0)
            elif choice.lower() == 'help':
                self.display_help_menu()
                continue
            try:
                index = int(choice) - 1
                categories = list(self.links.keys())
                if 0 <= index < len(categories):
                    self.display_links(categories[index])
                else:
                    print(f"{Fore.RED}Invalid selection. Please try again.")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.")

    def run(self):
        # URL of the GitHub README.md file
        readme_url = 'https://github.com/sourceduty/ChatGPT/blob/main/README.md'
        # Fetch the README content
        readme_content = self.fetch_readme(readme_url)
        if readme_content:
            self.extract_expected_link_count(readme_content)  
            self.extract_links(readme_content)  
            self.display_statistics()  
            print(f"{Fore.YELLOW}{'-' * 40}")  
            self.display_help_menu()  
            print(f"{Fore.YELLOW}{'-' * 40}")  
            self.select_category()  

if __name__ == "__main__":
    viewer = ReadMeViewer()
    viewer.run()
