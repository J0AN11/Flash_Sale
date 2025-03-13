# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 19:52:01 2025

@author: johan
"""

import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import time
import os
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PRODUCT_URL = os.getenv("PRODUCT_URL", "https://www.example.com/product-page")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "your-affiliate-tag")  # Amazon/Flipkart Affiliate Tag
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
TARGET_PRICE = float(os.getenv("TARGET_PRICE", 5000))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 900))  # Check every 15 minutes
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Function to generate affiliate link
def generate_affiliate_link(url):
    if "amazon" in url:
        return url + f"?tag={AFFILIATE_TAG}"  # Amazon Affiliate Structure
    elif "flipkart" in url:
        return f"https://www.flipkart.com?affid={AFFILIATE_TAG}"  # Flipkart Affiliate Structure
    return url  # Default to original URL if no affiliate match

# Function to get product price
def get_price():
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(PRODUCT_URL, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract price (Modify selector based on website structure)
        price_element = soup.find("span", {"class": "product-price"})
        if price_element:
            try:
                price = float(price_element.text.replace("₹", "").replace(",", ""))
                return price
            except ValueError:
                print("Error converting price to float.")
                return None
    else:
        print(f"Failed to fetch page, status code: {response.status_code}")
    return None

# Function to send email alert
def send_email(price):
    try:
        affiliate_link = generate_affiliate_link(PRODUCT_URL)
        msg = EmailMessage()
        msg['Subject'] = "Price Drop Alert!"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg.set_content(f"Good news! The product is now available at ₹{price}. Check it out: {affiliate_link}")
        
        # SMTP Configuration (Example: Gmail SMTP)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to send Telegram alert
def send_telegram_alert(price):
    affiliate_link = generate_affiliate_link(PRODUCT_URL)
    message = f"🔥 Price Drop Alert! 🔥\n\nProduct is now available at ₹{price}.\n\nCheck it out: {affiliate_link}"
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        print("Telegram alert sent!")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# Main Function
def check_price():
    while True:
        price = get_price()
        if price:
            print(f"Current Price: ₹{price}")
            if price <= TARGET_PRICE:
                send_email(price)
                send_telegram_alert(price)
                break
        else:
            print("Price data not available.")
        time.sleep(CHECK_INTERVAL)  # Wait before checking again

if __name__ == "__main__":
    check_price()
