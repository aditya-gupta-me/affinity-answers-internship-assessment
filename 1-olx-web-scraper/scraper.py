from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from tabulate import tabulate
import time
import re
import os

def is_relevant_car_cover(title, price):
    """
    Determine if a listing is an actual car cover product based on text and price.
    This helps filter out unrelated items such as property listings or electronics.
    
    Args:
        title (str): The product title/name
        price (str): The product price with currency symbol
    
    Returns:
        bool: True if the item is a relevant car cover, False otherwise
    """
    title_lower = title.lower()
    
    # Keywords that indicate irrelevant listings (real estate, electronics, etc.)
    exclude_keywords = [
        'bhk', 'flat', 'apartment', 'house', 'villa', 'sqft', 'sq ft', 'sq.ft',
        'parking for rent', 'parking for sale', 'floor', 'room', 'property',
        'rent', 'sale at', 'urgent sale', 'for urgent', 'iphone', 'phone',
        'mobile', 'laptop', 'led', 'tv', 'furniture', 'sofa'
    ]
    
    # Check if title contains any excluded keywords
    for keyword in exclude_keywords:
        if keyword in title_lower:
            return False
    
    # Filter out listings with unusually high prices that are unlikely to be car covers
    try:
        # Remove currency symbols and commas, then convert to integer
        price_str = price.replace('₹', '').replace(',', '').strip()
        if price_str and price_str != 'Not specified':
            price_num = int(re.sub(r'[^\d]', '', price_str))
            # Car covers typically cost less than ₹50,000
            if price_num > 50000:
                return False
    except:
        # If price parsing fails, continue with text-based filtering
        pass
    
    # Listing must contain both car-related and cover-related terminology
    car_terms = ['car', 'vehicle', 'auto']
    cover_terms = ['cover', 'body cover', 'seat cover', 'rain cover', 'dust cover']
    
    has_car_term = any(term in title_lower for term in car_terms)
    has_cover_term = any(term in title_lower for term in cover_terms)
    
    return has_car_term and has_cover_term

def scrape_olx_with_selenium(url):
    """
    Scrape OLX listings using Selenium with Firefox to handle dynamic content loading.
    Extracts title, price, description, location, and date from each listing.
    
    Args:
        url (str): The OLX search URL to scrape
    
    Returns:
        tuple: (listings, filtered_out) - Two lists containing relevant and filtered items
    """
    # Configure Firefox to run headless (without opening visible browser window)
    firefox_options = Options()
    firefox_options.add_argument('--headless')  # Run in background
    firefox_options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"
    )
    
    # Initialize the Selenium Firefox WebDriver
    try:
        # Automatically download and install geckodriver if needed
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
    except:
        # Fallback: Use system-installed geckodriver
        driver = webdriver.Firefox(options=firefox_options)
    
    # Initialize lists to store scraped data
    listings = []
    filtered_out = []
    
    try:
        print("Loading page with Firefox...")
        driver.get(url)
        
        # Allow sufficient time for JavaScript to render dynamic content
        print("Waiting for content to load...")
        time.sleep(8)
        
        # Scroll down progressively to trigger lazy-loaded items
        print("Scrolling to load more items...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        # Capture the fully rendered HTML source code
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Attempt multiple CSS selectors to extract listing elements
        # Method 1: Search by OLX-specific data attribute
        ads = soup.find_all('li', {'data-aut-id': 'itemBox'})
        
        # Method 2: Search by class name pattern (fallback if Method 1 fails)
        if not ads:
            ads = soup.find_all('li', class_=re.compile('.*_1DNjI.*|.*EIR5N.*'))
        
        # Method 3: Find all <li> tags containing item links (last resort)
        if not ads:
            all_li = soup.find_all('li')
            ads = [li for li in all_li if li.find('a', href=re.compile('item'))]
        
        print(f"Found {len(ads)} total listings")
        print("Filtering relevant car cover products...\n")
        
        # Extract details from each listing and apply filtering logic
        for idx, ad in enumerate(ads, 1):
            try:
                # Extract title (product name)
                title_elem = ad.find('span', {'data-aut-id': 'itemTitle'})
                if not title_elem:
                    # Fallback: Try finding title in <a> or <span> tags
                    title_elem = ad.find('a') or ad.find('span')
                title = title_elem.get_text(strip=True) if title_elem else "N/A"
                
                # Extract price
                price_elem = ad.find('span', {'data-aut-id': 'itemPrice'})
                if not price_elem:
                    # Fallback: Search for text containing rupee symbol
                    price_text = ad.find(string=re.compile('₹'))
                    price = price_text.strip() if price_text else "Not specified"
                else:
                    price = price_elem.get_text(strip=True)
                
                # Extract product description (if available)
                desc_elem = ad.find('span', {'data-aut-id': 'itemDescription'})
                if not desc_elem:
                    # Try alternative selectors for description
                    desc_elem = ad.find('div', class_=re.compile('.*description.*', re.IGNORECASE))
                description = desc_elem.get_text(strip=True) if desc_elem else "No description available"
                
                # Extract location (city/area)
                location_elem = ad.find('span', {'data-aut-id': 'item-location'})
                location = location_elem.get_text(strip=True) if location_elem else "N/A"
                
                # Extract listing date (when the ad was posted)
                date_elem = ad.find('span', {'data-aut-id': 'item-date'})
                date = date_elem.get_text(strip=True) if date_elem else "N/A"
                
                # Validate that we have meaningful data before processing
                if title and title != "N/A" and len(title) > 5:
                    # Apply relevance filter to exclude irrelevant items
                    if is_relevant_car_cover(title, price):
                        # Add to relevant listings
                        listings.append({
                            'Title': title,
                            'Price': price,
                            'Description': description,
                            'Location': location,
                            'Date': date
                        })
                        print(f"  ✓ Added: {title[:60]}... - {price}")
                    else:
                        # Add to filtered out list for review
                        filtered_out.append({
                            'Title': title,
                            'Price': price,
                            'Description': description,
                            'Location': location,
                            'Date': date
                        })
            
            except Exception as e:
                # Skip listings that cause parsing errors
                continue
        
        # Display summary of scraping results
        print(f"\n✓ Successfully extracted {len(listings)} relevant car cover listings")
        print(f"✗ Filtered out {len(filtered_out)} unrelated or invalid listings")
        
    except Exception as e:
        # Handle any errors during the scraping process
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always close the browser to free up resources
        print("\nClosing browser...")
        driver.quit()
    
    return listings, filtered_out

def display_results(listings):
    """
    Display extracted listings in a formatted table layout using tabulate library.
    
    Args:
        listings (list): List of dictionaries containing product information
    """
    if not listings:
        print("\nNo relevant car cover listings found.")
        return
    
    # Prepare data for table display
    table_data = []
    for i, listing in enumerate(listings, 1):
        # Truncate long text to fit in table
        title = listing['Title'][:50] + '...' if len(listing['Title']) > 50 else listing['Title']
        description = listing['Description'][:40] + '...' if len(listing['Description']) > 40 else listing['Description']
        location = listing['Location'][:20] + '...' if len(listing['Location']) > 20 else listing['Location']
        
        table_data.append([
            i,
            title,
            listing['Price'],
            description,
            location,
            listing['Date']
        ])
    
    # Define table headers
    headers = ['#', 'Title', 'Price', 'Description', 'Location', 'Date']
    
    # Print formatted table
    print("\n" + "="*120)
    print("RELEVANT CAR COVER PRODUCTS")
    print("="*120)
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    print("="*120)
    print(f"\n✓ Total relevant listings: {len(listings)}")

def save_to_csv(listings):
    """
    Save extracted product data to a CSV file in the Output directory.
    Creates the directory if it doesn't exist.
    
    Args:
        listings (list): List of dictionaries containing product information
    """
    if not listings:
        print("No data available to write to CSV.")
        return

    # Create the 'Output' directory if it doesn't exist
    output_dir = 'Output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Define the CSV filename and full path
    filename = 'olx_car_covers.csv'
    file_path = os.path.join(output_dir, filename)

    # Write data to CSV file
    import csv
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        # Define CSV columns
        writer = csv.DictWriter(f, fieldnames=['Title', 'Price', 'Description', 'Location', 'Date'])
        writer.writeheader()  # Write column headers
        writer.writerows(listings)  # Write all rows

    print(f"✓ Output successfully saved to: {file_path}")

def show_filtered_items(filtered_out):
    """
    Display a sample of irrelevant items that were removed during filtering.
    Helps verify that the filtering logic is working correctly.
    
    Args:
        filtered_out (list): List of filtered items
    """
    if not filtered_out:
        print("\n✓ No items were filtered out.")
        return
    
    print("\n" + "-"*100)
    print("FILTERED OUT (Irrelevant Items)")
    print("-"*100)
    
    # Show first 10 filtered items
    for i, item in enumerate(filtered_out[:10], 1):
        print(f"{i}. {item['Title'][:70]} - {item['Price']}")
    
    # Indicate if there are more filtered items
    if len(filtered_out) > 10:
        print(f"... and {len(filtered_out) - 10} more filtered items")
    
    print("-"*100)

if __name__ == "__main__":
    # Define the OLX search URL for car covers
    url = "https://www.olx.in/items/q-car-cover?isSearchCall=true"
    
    # Display program header
    print("="*100)
    print("OLX Car Cover Scraper - Using Selenium (Firefox) with Smart Filtering")
    print("="*100)
    print(f"Target URL: {url}\n")
    
    # Execute the scraping process
    listings, filtered_out = scrape_olx_with_selenium(url)
    
    # Display results in formatted table
    display_results(listings)
    
    # Save results to CSV file
    save_to_csv(listings)
    
    # Optionally show filtered items for verification
    response = input("\nDo you want to see filtered out items? (y/n): ").lower()
    if response == 'y':
        show_filtered_items(filtered_out)