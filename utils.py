from flask import redirect, render_template, request, url_for
from models import db, Product, InventoryHistory
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def add_product(store_prefix):
    if request.method == 'POST':
        name = request.form.get('name', '')
        quantity = request.form.get('quantity', '0')
        purchase_price = request.form.get('purchase_price', '0.0')

        try:
            quantity = int(quantity)
            purchase_price = float(purchase_price)
            logging.debug(f"Received data - Name: {name}, Quantity: {quantity}, Purchase Price: {purchase_price}")
        except ValueError as e:
            logging.error(f"Value error: {e}")
            return "Invalid data format", 400

        try:
            product = Product.query.filter_by(name=name, store_prefix=store_prefix).first()
            if product:
                logging.debug(f"Product found. Current Quantity before: {product.total_quantity}")
                product.add_stock(quantity, purchase_price)
                logging.debug(f"Product updated. New Quantity: {product.total_quantity}")
            else:
                product = Product(name=name, store_prefix=store_prefix)
                db.session.add(product)
                product.add_stock(quantity, purchase_price)
                logging.debug(f"Added new product with Quantity: {product.total_quantity}")

            db.session.commit()
            return redirect(url_for('routes.index_' + store_prefix))

        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return "Internal server error", 500

    return render_template('add_product.html', store_prefix=store_prefix)


def sell_product(product_id, store_prefix):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        sale_price = float(request.form['sale_price'])
        platform = request.form.get('platform')  # Получение платформы

        try:

            product.sell_stock(quantity, sale_price, platform)
        except ValueError as e:
            return str(e)

        return redirect(url_for('routes.index_' + store_prefix))

    return render_template('sell_product.html', product=product, store_prefix=store_prefix)


def process_edit_transaction(history_id, store_prefix):
    transaction = InventoryHistory.query.get_or_404(history_id)

    if request.method == 'POST':
        new_quantity = int(request.form['quantity'])
        new_price = float(request.form['price'])

        product = Product.query.filter_by(name=transaction.product_name, store_prefix=store_prefix).first()

        if transaction.action == 'sale':
            product.total_quantity += transaction.quantity
            product.total_sales_amount -= transaction.quantity * transaction.price
            product.total_quantity -= new_quantity
            product.total_sales_amount += new_quantity * new_price

        elif transaction.action == 'purchase':
            product.total_quantity -= transaction.quantity
            product.total_purchase_amount -= transaction.quantity * transaction.price
            product.total_quantity += new_quantity
            product.total_purchase_amount += new_quantity * new_price

        transaction.quantity = new_quantity
        transaction.price = new_price

        db.session.commit()

        return redirect(url_for('routes.index_' + store_prefix))

    return render_template('edit_transaction.html', transaction=transaction, store_prefix=store_prefix)


def update_product_name(product_id, new_name, store_prefix):
    product = Product.query.filter_by(id=product_id, store_prefix=store_prefix).first()

    if not product:
        print(f"Product with ID {product_id} not found for store {store_prefix}")
        return

    old_name = product.name
    product.name = new_name

    history_records = InventoryHistory.query.filter_by(product_name=old_name, store_prefix=store_prefix).all()
    print(f"Found {len(history_records)} history records to update for store {store_prefix}")

    if not history_records:
        print(f"No history records found for product {old_name} in store {store_prefix}")

    for record in history_records:
        record.product_name = new_name
        print(f"Updated record {record.id} in history to new name {new_name}")

    db.session.commit()
    print(f"Updated product name to {new_name} and committed changes.")
