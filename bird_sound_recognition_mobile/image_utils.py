from duckduckgo_search import DDGS
from typing import Optional

def get_bird_image_url(bird_name_zh: str) -> Optional[str]:
    """
    Get the main image URL for a bird species using DuckDuckGo Search.
    """
    try:
        with DDGS() as ddgs:
            # Search for images with the bird name
            # keywords: bird name + "bird" to be sure, or just the name
            keywords = f"{bird_name_zh} 鸟"
            results = list(ddgs.images(keywords, max_results=1))
            
            if results:
                return results[0]['image']
            
            return None
        
    except Exception as e:
        print(f"Error fetching image for {bird_name_zh}: {e}")
        return None

if __name__ == "__main__":
    # Test
    name = "麻雀"
    print(f"Fetching image for {name}...")
    url = get_bird_image_url(name)
    print(f"URL: {url}")
