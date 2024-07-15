from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

# Define the base class for declarative models
Base = declarative_base()

# Define the Product model
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)

    orders = relationship('Order', back_populates='product')

# Define the Order model
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_date = Column(DateTime, default=datetime.datetime.now())

    product = relationship('Product', back_populates='orders')
    bill = relationship('Bill', back_populates='order', uselist=False)

# Define the Bill model
class Bill(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    billing_date = Column(DateTime, default=datetime.datetime.now())

    order = relationship('Order', back_populates='bill')

# Create an SQLite database
engine = create_engine('sqlite:///ecommerce.db')

# Create all tables
Base.metadata.create_all(engine)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Example data
def populate_data():
    # Add products
    products = [
        Product(name='Laptop', price=1000.00, description='A high performance laptop'),
        Product(name='Smartphone', price=500.00, description='A latest model smartphone'),
        Product(name='Headphones', price=100.00, description='Noise-cancelling headphones'),
        Product(name='Tablet', price=300.00, description='A portable tablet'),
        Product(name='Camera', price=800.00, description='A professional camera'),
        Product(name='Printer', price=200.00, description='A high-quality printer'),
        Product(name='Monitor', price=400.00, description='A large computer monitor'),
        Product(name='Keyboard', price=50.00, description='A mechanical keyboard'),
        Product(name='Mouse', price=30.00, description='An ergonomic mouse'),
        Product(name='Speakers', price=150.00, description='High-fidelity speakers'),
        Product(name='External Hard Drive', price=120.00, description='A large capacity external hard drive'),
        Product(name='Wireless Earbuds', price=80.00, description='Bluetooth wireless earbuds'),
        Product(name='Gaming Console', price=400.00, description='A popular gaming console'),
        Product(name='Smart Watch', price=250.00, description='A feature-rich smart watch'),
        Product(name='Fitness Tracker', price=100.00, description='A wearable fitness tracker')
    ]


    session.add_all(products)
    session.commit()

    # Add orders
    orders = [
        Order(product_id=products[0].id, quantity=2),
        Order(product_id=products[1].id, quantity=1),
        Order(product_id=products[2].id, quantity=3),
        Order(product_id=products[3].id, quantity=2),
        Order(product_id=products[4].id, quantity=1),
        Order(product_id=products[5].id, quantity=3),
        Order(product_id=products[6].id, quantity=2),
        Order(product_id=products[7].id, quantity=1),
        Order(product_id=products[8].id, quantity=5),
        Order(product_id=products[9].id, quantity=8)
    ]

    session.add_all(orders)
    session.commit()

    # Add bills
    bills = [
        Bill(order_id=orders[0].id, total_amount=orders[0].quantity * products[0].price),
        Bill(order_id=orders[1].id, total_amount=orders[1].quantity * products[1].price),
        Bill(order_id=orders[2].id, total_amount=orders[2].quantity * products[2].price),
        Bill(order_id=orders[3].id, total_amount=orders[3].quantity * products[3].price),
        Bill(order_id=orders[4].id, total_amount=orders[4].quantity * products[4].price),
        Bill(order_id=orders[5].id, total_amount=orders[5].quantity * products[5].price),
        Bill(order_id=orders[6].id, total_amount=orders[6].quantity * products[6].price),
        Bill(order_id=orders[7].id, total_amount=orders[7].quantity * products[7].price),
        Bill(order_id=orders[8].id, total_amount=orders[8].quantity * products[8].price),
        Bill(order_id=orders[9].id, total_amount=orders[9].quantity * products[9].price)
    ]

    session.add_all(bills)
    session.commit()

if __name__ == '__main__':
    # Populate the database with example data
    populate_data()

    # Query the database
    products = session.query(Product).all()
    for product in products:
        print(f'Product: {product.name}, Price: {product.price}')

    orders = session.query(Order).all()
    for order in orders:
        print(f'Order: Product ID {order.product_id}, Quantity: {order.quantity}, Order Date: {order.order_date}')

    bills = session.query(Bill).all()
    for bill in bills:
        print(f'Bill: Order ID {bill.order_id}, Total Amount: {bill.total_amount}, Billing Date: {bill.billing_date}')

    # Close the session
    session.close()
