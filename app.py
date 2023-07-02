from flask import Flask, jsonify, request
import stripe
import os
from dotenv import load_dotenv
import logging

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

    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
      # Use an existing Customer ID if this is a returning customer
    customer = stripe.Customer.create()
    logger.info("Created Stripe Customer")
    ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2022-11-15',
    )
    logger.info("Created Stripe ephemeralKey")

    # Read the amount from the request body
    data = request.get_json()
    amount = data.get('amount')  # Default to 0 if amount is not provided
    logger.info(f"Amount: {amount}")
    logger.info(f"Amount type: {type(amount)}")
    paymentIntent = stripe.PaymentIntent.create(
        amount=amount*100,
        currency='eur',
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
