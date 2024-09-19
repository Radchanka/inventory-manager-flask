from flask import Blueprint, render_template, request, redirect, url_for
from models import db, Product, InventoryHistory
from utils import add_product, sell_product, process_edit_transaction, update_product_name

routes = Blueprint('routes', __name__)


@routes.route('/')
def main_page():
    total_purchase_amount = db.session.query(db.func.sum(Product.total_purchase_amount)).scalar() or 0
    total_sales_amount = db.session.query(db.func.sum(Product.total_sales_amount)).scalar() or 0
    total_difference = total_sales_amount - total_purchase_amount
    return render_template('main.html', total_purchase_amount=total_purchase_amount,
                           total_sales_amount=total_sales_amount,
                           total_difference=total_difference)


@routes.route('/pl/')
def index_pl():
    products = Product.query.filter_by(store_prefix='pl').all()
    total_purchase_amount = db.session.query(db.func.sum(Product.total_purchase_amount)).filter_by(store_prefix='pl').scalar() or 0
    total_sales_amount = db.session.query(db.func.sum(Product.total_sales_amount)).filter_by(store_prefix='pl').scalar() or 0
    total_difference = total_sales_amount - total_purchase_amount
    return render_template('index.html', products=products, store_prefix='pl',
                           total_purchase_amount=total_purchase_amount,
                           total_sales_amount=total_sales_amount,
                           total_difference=total_difference)


@routes.route('/ua/')
def index_ua():
    products = Product.query.filter_by(store_prefix='ua').all()
    total_purchase_amount = db.session.query(db.func.sum(Product.total_purchase_amount)).filter_by(store_prefix='ua').scalar() or 0
    total_sales_amount = db.session.query(db.func.sum(Product.total_sales_amount)).filter_by(store_prefix='ua').scalar() or 0
    total_difference = total_sales_amount - total_purchase_amount
    return render_template('index.html', products=products, store_prefix='ua',
                           total_purchase_amount=total_purchase_amount,
                           total_sales_amount=total_sales_amount,
                           total_difference=total_difference)


@routes.route('/pl/add_product', methods=['GET', 'POST'])
def add_product_pl():
    return add_product('pl')


@routes.route('/ua/add_product', methods=['GET', 'POST'])
def add_product_ua():
    return add_product('ua')


@routes.route('/pl/sell_product/<int:product_id>', methods=['GET', 'POST'])
def sell_product_pl(product_id):
    return sell_product(product_id, 'pl')


@routes.route('/ua/sell_product/<int:product_id>', methods=['GET', 'POST'])
def sell_product_ua(product_id):
    return sell_product(product_id, 'ua')


@routes.route('/history')
def view_history():
    purchases = InventoryHistory.query.filter_by(action='purchase').order_by(InventoryHistory.timestamp.desc()).all()
    sales = InventoryHistory.query.filter_by(action='sale').order_by(InventoryHistory.timestamp.desc()).all()
    return render_template('history.html', purchases=purchases, sales=sales)


@routes.route('/edit_transaction/<int:history_id>/<string:store_prefix>', methods=['GET', 'POST'])
def edit_transaction(history_id, store_prefix):
    return process_edit_transaction(history_id, store_prefix)


@routes.route('/edit_product_name_page/<string:store_prefix>/<int:product_id>', methods=['GET', 'POST'])
def edit_product_name_page(store_prefix, product_id):
    product = Product.query.filter_by(id=product_id, store_prefix=store_prefix).first()

    if request.method == 'POST':
        new_name = request.form['name']
        print(f"Updating product name to {new_name} for store {store_prefix}")
        update_product_name(product_id, new_name, store_prefix)
        return redirect(url_for('routes.index_' + store_prefix))

    return render_template('edit_product_name.html', product=product, store_prefix=store_prefix)
