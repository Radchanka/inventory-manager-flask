from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_quantity = db.Column(db.Integer, default=0)
    total_purchase_amount = db.Column(db.Float, default=0.0)
    total_sales_amount = db.Column(db.Float, default=0.0)
    store_prefix = db.Column(db.String(10), nullable=False)

    def add_stock(self, quantity, purchase_price):
        if self.total_quantity is None:
            self.total_quantity = 0
        if self.total_purchase_amount is None:
            self.total_purchase_amount = 0.0
        self.total_quantity += quantity
        self.total_purchase_amount += quantity * purchase_price

        db.session.commit()

        history_entry = InventoryHistory(
            action='purchase',
            product_name=self.name,
            quantity=quantity,
            price=purchase_price,
            store_prefix=self.store_prefix
        )
        db.session.add(history_entry)
        db.session.commit()

    def sell_stock(self, quantity, sale_price, platform=None):
        if quantity > self.total_quantity:
            raise ValueError("Недостаточно товара на складе.")
        if self.total_sales_amount is None:
            self.total_sales_amount = 0.0
        self.total_quantity -= quantity
        self.total_sales_amount += quantity * sale_price

        db.session.commit()

        history_entry = InventoryHistory(
            action='sale',
            product_name=self.name,
            quantity=quantity,
            price=sale_price,
            store_prefix=self.store_prefix,
            platform=platform
        )
        db.session.add(history_entry)
        db.session.commit()


class InventoryHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    store_prefix = db.Column(db.String(10), nullable=False)
    platform = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
