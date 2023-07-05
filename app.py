from flask import Flask, jsonify, request
import stripe
import os
from dotenv import load_dotenv
import logging
import json

app = Flask(__name__)

# Create a logger object
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Set log level to INFO. Change it to DEBUG, ERROR, WARN as per your requirement.

# Load environment variables from a .env file
def configure_secrets():
    load_dotenv()
    logger.info("Environment Variables Loaded")

configure_secrets()

# This example sets up an endpoint using the Flask framework.
# Watch this video to get started: https://youtu.be/7Ul1vfmsDck.

@app.route('/payment-sheet', methods=['POST'])
def payment_sheet():
    # Set your secret key. Remember to switch to your live secret key in production.
    # See your keys here: https://dashboard.stripe.com/apikeys

    logger.info("Got payment request")

    # Read the email and amount from the request body
    data = request.get_data().decode('utf-8')
    data_dict = json.loads(data)
    # email = data_dict['email']
    # logger.info(f"customer's email: {email}")

    product_prices = {
        "always": 3.49,
        "cup1": 9.99,
        "cup2": 7.99,
        "cup3": 6.49,
        "durex1": 5.99,
        "durex2": 6.99,
        "faceplate": 4.99,
        "pt1": 2.99,
        "pt2": 3.99,
        "pt3": 4.49,
        "t1": 1.99
    }

    products = data_dict['products']
    logger.info(f"products ordered: {products}")

    total_amount = 0

    for product_dict in products:
        for product, quantity in product_dict.items():
            if product in product_prices:
                price = product_prices[product]
                total_amount += price * quantity

    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    # Use an existing Customer ID if this is a returning customer
    # customer = stripe.Customer.create(email=email)
    customer = stripe.Customer.create()
    logger.info("Created Stripe Customer")

    ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2022-11-15',
    )
    logger.info("Created Stripe ephemeralKey")

    paymentIntent = stripe.PaymentIntent.create(
        amount=int(total_amount * 100),
        currency='pln',
        customer=customer['id'],
        automatic_payment_methods={
          'enabled': True,
        },
    )
    logger.info("Created Stripe paymentIntent")

    logger.info(f"Returning response: {jsonify(paymentIntent=paymentIntent.client_secret, ephemeralKey=ephemeralKey.secret, customer=customer.id, publishableKey=os.getenv('STRIPE_PUBLISHABLE_KEY'))}")

    return jsonify(paymentIntent=paymentIntent.client_secret,
                   ephemeralKey=ephemeralKey.secret,
                   customer=customer.id,
                   publishableKey=os.getenv('STRIPE_PUBLISHABLE_KEY')
                   )

if __name__ == '__main__':
    app.run()
