from flask import render_template, redirect, url_for, jsonify
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
    try:
        # Fetch the list of products from Stripe
        products = stripe.Product.list(limit=100)
        logger.debug("Fetched product list")

        # Fetch the list of prices from Stripe
        prices = stripe.Price.list(limit=100)
        logger.debug("Fetched price list")

        # Fetch the list of payment links from Stripe (if available)
        # Note: Adjust if the API or method to fetch payment links is different
        payment_links = stripe.PaymentLink.list(limit=100) if hasattr(stripe, 'PaymentLink') else []
        logger.debug("Fetched payment links list")

        # Create a list to hold product details
        product_list = []

        # Loop through each product
        for product in products.data:
            if product.active:
                # Get the price for the current product
                price_info = next((price for price in prices.data if price.product == product.id), None)
                    

                # Get the payment link for the current product
                
                if price_info and price_info['unit_amount']!=None:
                    payment_link = stripe.PaymentLink.create(
                        line_items=[{'price': price_info.id, 'quantity': 1}],
                        shipping_address_collection={
                            'allowed_countries': ['US', 'CA', 'MX'],  # Restrict shipping to US, CA, and MX
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
                    logger.debug("****************************************")
                    

                    logger.debug("****************************************")
                    #logger.debug(f"Product: {product.name}, Price: {price_info.unit_amount}, Payment Link: {payment_link_info.url}")
                    logger.debug(payment_link_info['url'])
                    logger.debug("****************************************")

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

        # Render the store page with the product list
        return render_template('store.html', products=product_list)
    
    except Exception as e:
        logger.error(f"Error fetching products: {e}", exc_info=True)
        return f"An error occurred: {e}", 500
    
    except Exception as e:
        print(f"Error fetching products: {e}")
        return f"An error occurred: {e}"
        return f"An error occurred: {e}", 500
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

@main.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = stripe.Product.list(limit=100)
        prices = stripe.Price.list(limit=100)

        product_list = []
        category_set = set()

        price_dict = {price.product: price for price in prices.data}

        for product in products.data:
            if product.active:
                price_info = price_dict.get(product.id)
                if price_info:
                    sizes = product.metadata.get('sizes', '').split(', ') if 'sizes' in product.metadata else []

                    product_list.append({
                        'id': product.id,
                        'name': product.name,
                        'description': product.description,
                        'images': product.images,
                        'price': price_info.unit_amount / 100,  # Convert cents to dollars
                        'sizes': sizes,
                        'buy_link': price_info.url,
                        'category_id': product.metadata.get('category', 'default')
                    })

                    category_set.add(product.metadata.get('category', 'default'))

        category_list = [{'id': category, 'name': category} for category in category_set]

        return jsonify({
            'categories': category_list,
            'products': product_list
        })

    except Exception as e:
        logging.error(f"Error fetching products: {e}")
        return jsonify({'error': str(e)}), 500

@main.route('/store/<product_id>')
def store_product(product_id):
    try:
        # Fetch data from the API
        response = requests.get('http://localhost:5000/api/products')
        data = response.json()

        # Find the specific product based on the product_id
        product = next((prod for prod in data['products'] if prod['id'] == product_id), None)

        if product:
            return render_template('product.html', product=product)
        else:
            return "Product not found", 404
    except Exception as e:
        return f"An error occurred: {e}"

@main.route('/memes')
def memes():
    # List of image URLs
    image_urls = [
        "https://i.ibb.co/8K9YVTV/image.webp",
        "https://i.ibb.co/8K9YVTV/image.webp",
        "https://i.ibb.co/ynCnX46/battle.webp"
    ]
    return render_template('memes.html', image_urls=image_urls)