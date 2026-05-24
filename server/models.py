# Import all modules and utilities
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

# Create the db for Flask to connect to
db = SQLAlchemy(metadata=metadata)

# Create a class model to dictate who buys what per review
class Customer(db.Model):

    # Which table this model is connected to
    __tablename__ = 'customers'

    # Create unique id for each customer
    id = db.Column(db.Integer, primary_key=True)
    # Create other needed attributes for the model
    name = db.Column(db.String)

    # One customer might have many review so its a one to many
    reviews = db.relationship("Review", back_populates = "customer", cascade = "all, delete-orphan")

    # Don't forget to include association proxy to skip through other reviews if necessary
    items = association_proxy("reviews", "item")

    # Provide string when customer is printed
    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'

# Create an item model that dictates product reviews by which customer
class Item(db.Model):

    # Which table this model is connected to
    __tablename__ = 'items'

    # Create unique id for each item
    id = db.Column(db.Integer, primary_key=True)
    # Create other needed attributes for the model
    name = db.Column(db.String)
    price = db.Column(db.Float)

    # One item will have many review so its a one to many 
    reviews = db.relationship("Review", back_populates = "item", cascade = "all,delete-orphan")

    # Don't forget to include association proxy to skip through other reviews if necessary
    customers = association_proxy("reviews", "customer")
    
    # Provide string when item is printed
    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'
    
# Create an review model to join customers to items with necessary information
class Review(db.Model):

    # Which table this model is connected to
    __tablename__ = 'reviews'

    # Create unique id for each review
    id = db.Column(db.Integer, primary_key=True)
    # Create other needed attributes for the model
    comment = db.Column(db.String)

    # A foreign key is needed to link the reviews to customers  
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))

    # Each review needs to be mappe to one item
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))

    # Each review will map to one customer but there will be many reviews to one customer
    customer = db.relationship('Customer', back_populates='reviews')

    # Each review will map to one item but there will be many reviews to one item
    item = db.relationship('Item', back_populates='reviews')

    # Provide string when review is printed
    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'

# Create a class to provide CustomerSchema to convert customer objects to dicts
class CustomerSchema(Schema):
    # Serialize the columns
    id = fields.Int() 
    name = fields.Str() 

    # Serialize the reviews relationship
    reviews = fields.List(fields.Nested(lambda: ReviewSchema(exclude=('customer',))))

    # Serialize the items association proxy
    items = fields.List(fields.Nested(lambda: ItemSchema(exclude=('customers', 'reviews'))))

# Create a class to convert item objects to dicts
class ItemSchema(Schema):
    # Serialize the columns
    id = fields.Int() 
    name = fields.Str() 
    price = fields.Float()

    # Serialize the reviews relationship
    reviews = fields.List(fields.Nested(lambda: ReviewSchema(exclude=('item',))))

    # Serialize the customer association proxy
    customers = fields.List(fields.Nested(lambda: CustomerSchema(exclude=('items', 'reviews'))))

# Create a class to convert review objects to dicts
class ReviewSchema(Schema):
    # Serialize the columns
    id = fields.Int() 
    comment = fields.Str() 

    # Serialize the customer relationship
    customer = fields.Nested(lambda: CustomerSchema(exclude=('reviews', 'items')))

    # Serialize the item relationship
    item = fields.Nested(lambda: ItemSchema(exclude=('reviews', 'customers')))

# Declare all necessary schemas for all routes and tests
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)
