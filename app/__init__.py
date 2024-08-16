from flask import Flask
from .main import main as main_blueprint
from .auth import auth as auth_blueprint
import logging
import stripe
product_list = []
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_product_list():
    try:
        # Fetch the list of products from Stripe
        products = stripe.Product.list(limit=100)
        logger.debug("Fetched product list")

        # Fetch the list of prices from Stripe
        prices = stripe.Price.list(limit=100)
        logger.debug("Fetched price list")

        # Fetch the list of payment links from Stripe (if available)
        payment_links = stripe.PaymentLink.list(limit=100) if hasattr(stripe, 'PaymentLink') else []
        logger.debug("Fetched payment links list")

        # Create a list to hold product details
        product_list = []

        # Loop through each product
        for product in products.data:
            if product.active:
                # Get the price for the current product
                price_info = next((price for price in prices.data if price.product == product.id), None)
                
                if price_info and price_info['unit_amount'] is not None:
                    # Create payment link
                    payment_link = stripe.PaymentLink.create(
                        line_items=[{'price': price_info.id, 'quantity': 1}],
                        shipping_address_collection={
                            'allowed_countries': ['US', 'CA', 'MX'],
                        },
                        automatic_tax={'enabled': True},
                        custom_fields=[
                            {
                                'key': 'size',
                                'label': {'type': 'custom', 'custom': 'Size'},
                                'type': 'dropdown',
                                'dropdown': {
                                    'options': [
                                        {'label': 'S', 'value': 's'},
                                        {'label': 'M', 'value': 'm'},
                                        {'label': 'L', 'value': 'l'},
                                        {'label': 'XL', 'value': 'xl'},
                                        {'label': '2XL', 'value': '2xl'}
                                    ]
                                }
                            }
                        ]
                    )
                    payment_link_info = payment_link

                    # Append the product details with price and payment link
                    product_list.append({
                        'id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'images': product.images,
                        'price': price_info['unit_amount'] / 100,  # Convert from cents to dollars
                        'buy_url': payment_link_info['url'],  # Use 'buy_url' to avoid confusion with the price URL
                    })
                else:
                    logger.warning(f"Missing price or payment link info for product ID: {product.id}")

        return product_list

    except Exception as e:
        logger.error(f"Error fetching products: {e}", exc_info=True)
        return None
def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    global product_list
    product_list = fetch_product_list()
    app.config['PRODUCT_LIST'] = product_list
    return app
