from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


pages = 20
# JavaScript code to execute on each page
js_code_isbn_price = """
const elementsWithItemId = document.querySelectorAll(`[data-cnstrc-item-id]`);

// Array to store the cleaned values of 'data-cnstrc-item-id'
const itemIds = [];
const bookDetails = [];

// Iterate over each selected element to get the attribute value
elementsWithItemId.forEach(element => {
  // Get the value of 'data-cnstrc-item-id'
  let itemId = element.getAttribute('data-cnstrc-item-id');
  // Remove the trailing 'B' if present
  if (itemId.endsWith('B')) {
    itemId = itemId.slice(0, -1);
  }

  // Check the list price within the element
  const priceElement = element.querySelector('.jss148');
    let currentPriceElement = element.querySelector('.jss162');

    if (!currentPriceElement) {
        currentPriceElement = element.querySelector('.jss147');
    }
 const bookTypeElement = element.querySelector('.jss146');

  if (priceElement && currentPriceElement) {
    // Extract the text content of the price element
    const listPriceText = priceElement.textContent.trim();
    const currentPrice= currentPriceElement.textContent.trim();
    const bookType = bookTypeElement.textContent.trim();

    // Use a regular expression to find the price in the text
    const priceMatch = listPriceText.match(/List price:\s*\$(\d+(\.\d{2})?)/);

    // If a match is found and the list price is greater than $30
    if (priceMatch && parseFloat(priceMatch[1]) > 10) {
      // Add the cleaned value to the array
       // If an ISBN number is found and price element exists, add to the array
        if (itemId && priceMatch) {
            const isbn = itemId; // Get the matched ISBN
            const price = priceElement.textContent.trim().replace('List price: $', '').replace(',', ''); // Clean price
            bookDetails.push({ isbn, price ,currentPrice, bookType});
        }    }
  }
});
return bookDetails;
"""


def get_thrift_store_data(driver, pages=pages):
    base_url = 'https://bookoutlet.com/books?sort_by=arrival_date&sort_order=descending'

    current_page = 1
    thrift_store_data = []

    while current_page <= pages:
        print(f'Navigating to page {current_page}...')
        url = f"{base_url}&page={current_page}"
        driver.get(url)
        time.sleep(2)  # Wait for the page to load

        # Get book details from the Book Store
        isbn_numbers_price = driver.execute_script(js_code_isbn_price)
        thrift_store_data.extend(isbn_numbers_price)
        current_page += 1  # Increment the page counter

    return thrift_store_data


def get_sales_rank(driver):
    try:
        element2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                    "//span[@class='a-text-bold' and contains(text(), 'Best Sellers Rank:')]")
            )
        )

        # Locate the parent element which contains the full text
        parent_element = element2.find_element(By.XPATH, "..")
        full_text = parent_element.text

        # Use regular expression to extract the rank number
        match = re.search(r'#([\d,]+) in Books', full_text)
        if match:
            best_sellers_rank = match.group(1).replace(',', '')
            return best_sellers_rank
    except Exception:
        return 0


def get_amazon_price(isbn, bookType, driver):
    url = f'https://www.amazon.com/dp/{isbn}'
    driver.get(url)

    try:
        # # Wait for the price element to be present
        # price_whole = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, 'span.slot-price'))
        # )
        if 'hardcover' in bookType.lower():
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, 'tmm-grid-swatch-HARDCOVER'))
            )
        else:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.ID, 'tmm-grid-swatch-PAPERBACK'))
            )

        # Within this element, find the span with the class 'slot-price'
        price_whole = element.find_element(
            By.CSS_SELECTOR, 'span.slot-price span.a-size-base.a-color-price.a-color-price')

        if price_whole:
            price_text = price_whole.text.strip().replace(',', '')
            return price_text  # Return as string for further checking
        else:
            return 'No price found'  # Return this message if no price found

    except Exception:
        return 'No price found'  # Return this message for any exception


def isbn13_to_isbn10(isbn13):
    # Ensure the input is a string
    isbn13 = str(isbn13)

    # Check if the ISBN-13 starts with '978'
    if not isbn13.startswith('978'):
        raise ValueError(
            "Only ISBN-13 starting with '978' can be converted to ISBN-10")

    # Extract the relevant part (remove the '978' prefix and the last digit)
    isbn10_base = isbn13[3:-1]

    # Compute the checksum for ISBN-10
    checksum = sum((i + 1) * int(digit)
                   for i, digit in enumerate(isbn10_base)) % 11

    # If the checksum is 10, the check digit is 'X'
    check_digit = 'X' if checksum == 10 else str(checksum)

    # Construct the ISBN-10
    isbn10 = isbn10_base + check_digit
    return isbn10


def main():
    driver = webdriver.Chrome()

    try:
        thrift_store_data = get_thrift_store_data(driver, pages=pages)

        matching_isbns = []  # List to store ISBNs that meet the condition

        for book in thrift_store_data:
            isbn = book['isbn']
            bookType = book['bookType']

            currentPriceText = book['currentPrice'].replace('$', '')
            try:
                currentPrice = float(currentPriceText)
            except Exception:
                currentPrice = 0

            thrift_price_str = book['price'].replace('from $', '').replace(
                ',', '').strip()  # Clean up thrift price

            # Handle potential price ranges (e.g., '9.95 - $10.64')
            if ' - ' in thrift_price_str:
                thrift_price_str = thrift_price_str.split(
                    ' - ')[0]  # Take the lower price

            # Convert to float
            try:
                thrift_price = float(
                    thrift_price_str) if thrift_price_str else 0.0
            except ValueError:
                print(
                    f'Error converting thrift price: "{thrift_price_str}" for ISBN: {isbn}')
                continue  # Skip this book if the price cannot be converted

            amazon_price = get_amazon_price(
                isbn13_to_isbn10(isbn), bookType, driver)
            sales_rank = get_sales_rank(driver)

            amazon_price = amazon_price.replace('$', '')
            # Check if Amazon price is valid, does not contain '-', and compare
            if isinstance(amazon_price, str) and '-' in amazon_price:
                print(
                    f'Skipping ISBN: {isbn} due to Amazon price containing "-"')
                continue  # Skip if price contains '-'

            if isinstance(amazon_price, str):
                try:
                    # Convert to float if it's a valid number
                    amazon_price_float = float(amazon_price)
                except ValueError:
                    print(
                        f'Skipping ISBN: {isbn} due to invalid Amazon price: {amazon_price}')
                    continue  # Skip if unable to convert

                # Check if Amazon price is greater than four times the Book Store price
                if amazon_price_float > currentPrice * 3:  # Check for 400% increase
                    print(
                        f'ISBN: {isbn}, Current Price: ${currentPrice}, Amazon Price: ${amazon_price_float:.2f} <<<<<<')
                    # Store the matching ISBN

                    # Format the percentage to two decimal places and append it to matching_isbns
                    matching_isbns.append(
                        f"{isbn} - {currentPrice} - {amazon_price} - {sales_rank}(rank)"
                    )
                else:
                    print(
                        f'ISBN: {isbn},  Current Price: ${currentPrice}, Amazon Price: ${amazon_price_float:.2f}')
            else:
                print(
                    f'ISBN: {isbn},  Current Price: ${currentPrice}, Amazon Price: {amazon_price}')

        # Print all ISBNs that met the condition
        print("\nISBNs with Amazon price greater than 4 times the Book Store price:")
        for isbn in matching_isbns:
            print(isbn)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
