from flask import Flask, jsonify, request
import stripe
import os
from dotenv import load_dotenv
import logging
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = Flask(__name__)

# Create a logger object
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Set log level to INFO. Change it to DEBUG, ERROR, WARN as per your requirement.

# Load environment variables from a .env file
def configure_secrets():
    load_dotenv()
    logger.info("Environment Variables Loaded")

# Initialize Firebase Admin SDK
def initialize_firebase():
    firebase_credentials = credentials.Certificate('firebase_credentials.json')  # Replace with your service account key file path
    firebase_admin.initialize_app(firebase_credentials)

configure_secrets()
initialize_firebase()

logger.info("Firestore initialized")

# init db
db = firestore.client()

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

    product_prices_ref = db.collection('productPrices').limit(1)  # Replace with your document ID
    product_prices_doc = product_prices_ref.get()

    logger.info(f"product_prices_doc {product_prices_doc}")

    if not product_prices_doc.exists:
        logger.info("Product prices document not found")
        return jsonify(error="Product prices not available"), 404

    product_prices_data = product_prices_doc.to_dict()

    if not product_prices_data or 'productPrices' not in product_prices_data:
        logger.info("Product prices not found in document")
        return jsonify(error="Product prices not available"), 404

    product_prices = product_prices_data['productPrices']

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