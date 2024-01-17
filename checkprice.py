import requests
from bs4 import BeautifulSoup
import datetime
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define a list of URLs to monitor
urls_to_monitor = [
    'https://www.rei.com/product/216625/cannondale-caad13-disc-105-bike',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/van-rysel-edr-af105-road-bike-305449?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/triban-triban-grvl-520-subcompact-gravel-bike-326904',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/gravel-bike-bicycle?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/van-rysel-edr-cf-shimano-105-carbon-road-bike-with-disc-brakes-324411?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/triban-grvl900-shimano-grx-titanium-frame-gravel-bike-325632?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/triban-rc-500-disc-road-bike-306241?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/triban-rc100-adult-road-bike-700c-silver-xl-u307028?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/rc-120-disc-326838?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/road-bike-disc-105-rc-520?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/triban-women-easy-bike?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/woman-regular-triban-311819?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/triban-rc-500-road-bike-311749?',
    'https://www.decathlon.com/collections/road-gravel-bikes/products/triban-rc520-disc-brake-road-bike-womens-8629968-967269?',
    'https://www.rei.com/product/216625/cannondale-caad13-disc-105-bike',
    'https://www.rei.com//product/184749/salsa-journeyer-claris-700-bike',
    'https://www.rei.com//product/184748/salsa-journeyer-claris-650b-bike',
    'https://www.rei.com//product/208192/cannondale-topstone-3-bike',
    'https://www.rei.com//product/159859/co-op-cycles-adv-22-bike',
    'https://www.rei.com//product/184747/salsa-journeyer-apex-1-700c-bike',
    'https://www.rei.com//product/182628/cannondale-topstone-carbon-5-bike',
    'https://www.rei.com//product/228434/diamondback-haanjo-2-bike',
    'https://www.rei.com//product/190608/co-op-cycles-adv-23-bike',
    'https://www.rei.com//product/208190/cannondale-topstone-1-bike',
    'https://www.rei.com//product/184751/salsa-journeyer-sora-650b-bike',
    'https://www.rei.com//product/220761/co-op-cycles-adv-11-bike',
    'https://www.rei.com//product/205432/salsa-journeyer-advent-650b-bike',
    'https://www.rei.com//product/205433/salsa-journeyer-advent-700c-bike',
    'https://www.rei.com//product/182630/cannondale-topstone-neo-5-electric-bike',
    'https://www.rei.com//product/190168/cannondale-synapse-carbon-3-l-bike-2021',
    'https://www.rei.com//product/199794/salsa-cutthroat-grx-600-bike',
    'https://www.rei.com//product/186752/cannondale-topstone-neo-sl-2-electric-bike',
    'https://www.rei.com//product/208240/salsa-journeyer-grx-600-650b-bike',
    'https://www.rei.com//product/184509/cannondale-tesoro-neo-x-2-remixte-electric-bike',
    'https://www.rei.com//product/208193/cannondale-topstone-4-bike',
    'https://www.rei.com//product/208185/cannondale-topstone-carbon-4-bike',
    'https://www.rei.com//product/184508/cannondale-tesoro-neo-x-3-electric-bike',
    'https://www.rei.com//product/208189/cannondale-synapse-al-3-bike',
    'https://www.rei.com//product/199796/salsa-warbird-grx-610-1x-bike',
    'https://www.rei.com//product/180598/co-op-cycles-adv-31-bike',
    'https://www.rei.com//product/228435/diamondback-haanjo-3-bike',
    'https://www.rei.com//product/159858/co-op-cycles-adv-21-bike',
    'https://www.rei.com//product/184752/salsa-journeyer-sora-700c-bike',
    'https://www.rei.com//product/199798/salsa-warroad-c-105-bike',
    'https://www.walmart.com/ip/Decathlon-Triban-RC100-Adult-Road-Bike-700c-Silver-S/163847876?from=/search'
]
# Function to scrape the price from the webpage


def get_item_price():
    headers = {
        "User-Agent": "Your-User-Agent-String",
        "Referer": "https://example.com"
    }
    session = requests.Session()
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Use appropriate HTML tags and attributes to locate the item's price
        price_element = soup.find(
            'span', {'id': 'buy-box-product-price'})
        if price_element:
            return price_element.text.strip()
        else:
            price_element = soup.find(
                'span', {'class': 'js-de-PriceAmount'})
            if price_element:
                return price_element.text.strip()
            else:
                price_element = soup.find(
                    'span', {'itemprop': 'price'})
                if price_element:
                    return price_element.text.strip()
    return None

# Function to log the price to a CSV file with the date


def log_price(url, price):
    today = datetime.date.today()
    data_to_write = []

    with open('price_log.csv', 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        data_by_url = {row[0]: row for row in csv_reader}

    if url not in data_by_url or data_by_url[url][2] != price:
        # URL doesn't exist or the price has changed, add/update the entry
        data_by_url[url] = [url, str(today), price]
        data_to_write = list(data_by_url.values())
    else:
        # URL is new, add it as a new entry
        data_to_write = [[url, str(today), price]]
        # Write the updated data to the CSV file
    with open('price_log.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(data_to_write)
# Function to read CSV data into a dictionary


def read_csv_data():
    data_by_url = {}
    with open('price_log.csv', 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            if len(row) >= 3:  # Ensure the row has URL, Date, and Price columns
                url, date, price = row
                data_by_url[url] = {"Date": date, "Price": price}
    return data_by_url

# Function to send an email notification


def send_email(subject, message):
    # Replace with your email server settings and credentials
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'dailypricecheckv1@gmail.com'
    smtp_password = 'wprw rjjx gyag iutz'
    sender_email = 'dailypricecheckv1@gmail.com'
    recipient_email = 'alinail13.ank@gmail.com'

    # Create an SMTP connection
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Send the email
    server.sendmail(sender_email, recipient_email, msg.as_string())

    # Close the SMTP server connection
    server.quit()


if __name__ == "__main__":
    today = datetime.date.today()
    print(today)
    for url in urls_to_monitor:
        price = get_item_price()
        if price:
            # Check if the price has changed
            data_by_url = read_csv_data()
            if url in data_by_url:
                yesterday_price = data_by_url[url]["Price"]
                if price != yesterday_price:
                    subject = "Price Change Alert"
                    message = f"The price has changed from {yesterday_price} to {price}. Go to {url}"
                    send_email(subject, message)
                    log_price(url, price)
                    print(url + " Price changed." + yesterday_price +
                          " to " + price + " Email should have sent.")
                else:
                    print(url + " " + yesterday_price + " = " +
                          price + " >>> No change detected.")
            else:
                log_price(url, price)

        else:
            print("Price not found on the webpage")
