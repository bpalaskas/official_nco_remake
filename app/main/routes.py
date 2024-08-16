from flask import render_template, redirect, url_for, jsonify,current_app
from . import main
import stripe
import logging
import requests
logger = logging.getLogger(__name__)
stripe.api_key = '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'
images=[]



@main.route('/')
def index():
    return render_template('index.html')

@main.route('/store')
def store():
    product_list = current_app.config['PRODUCT_LIST']
    return render_template('store.html', products=product_list)

@main.route('/store/product-<id>')
def store_product(id):

    product_list = current_app.config['PRODUCT_LIST']
    product = next((p for p in product_list if p['id'] == id), None)
    return render_template('product.html', product=product)

    
    
@main.route('/mission')
def mission():
    return render_template('mission.html')

@main.route('/events')
def events():
    return render_template('events.html')

@main.route('/members')
def members():
    return render_template('members.html')

@main.route('/join')
def join():
    return render_template('join.html')

@main.route('/api/featured-products')
def get_featured_products():
    try:
        products = stripe.Product.list(limit=100)
        prices = stripe.Price.list(limit=100)

        featured_products = []
        price_dict = {price.product: price for price in prices.data}

        for product in products.data:
            if product.active and product.metadata.get('featured') == 'true':
                price_info = price_dict.get(product.id)
                if price_info:
                    sizes = product.metadata.get('sizes', '').split(', ') if 'sizes' in product.metadata else []

                    featured_products.append({
                        'id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'images': product.images,
                        'price': price_info.unit_amount / 100,
                        'sizes': sizes,
                        'buy_link': price_info.url,
                    })

        return jsonify(featured_products)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@main.route('/memes')
def memes():
    # List of image URLs
    image_urls = [
        "https://i.ibb.co/8K9YVTV/image.webp",
        "https://i.ibb.co/8K9YVTV/image.webp",
        "https://i.ibb.co/ynCnX46/battle.webp"
    ]
    return render_template('memes.html', image_urls=image_urls)

@main.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'product.created':
        product = event['data']['object']
        metadata = product.get('metadata', {})
        
        # Check if the product should be ignored based on metadata
        if metadata.get('Visibility') != 'IGNORE':
            # Fetch the updated product list and write to JSON file
            fetch_product_list()
            logger.info(f"Product {product['id']} updated.")
    
    return jsonify({'status': 'success'}), 200
