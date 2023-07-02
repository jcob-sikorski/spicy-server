from flask import Flask, jsonify
import stripe
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from a .env file
def configure_secrets():
    load_dotenv()

configure_secrets()

# This example sets up an endpoint using the Flask framework.
# Watch this video to get started: https://youtu.be/7Ul1vfmsDck.

@app.route('/payment-sheet', methods=['POST'])
def payment_sheet():
    # Set your secret key. Remember to switch to your live secret key in production.
    # See your keys here: https://dashboard.stripe.com/apikeys
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
      # Use an existing Customer ID if this is a returning customer
    customer = stripe.Customer.create()
    ephemeralKey = stripe.EphemeralKey.create(
        customer=customer['id'],
        stripe_version='2022-11-15',
    )
    paymentIntent = stripe.PaymentIntent.create(
        amount=2,
        currency='pln',
        customer=customer['id'],
        automatic_payment_methods={
          'enabled': True,
        },
    )
    return jsonify(paymentIntent=paymentIntent.client_secret,
                     ephemeralKey=ephemeralKey.secret,
                     customer=customer.id,
                     publishableKey=os.getenv('STRIPE_PUBLISHABLE_KEY')
    )

if __name__ == '__main__':
    app.run()
