from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    page_count = db.Column(db.Integer, nullable=False, default=1)

    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))

    @validates('page_count')
    def validate_pages(self, key, value):
        if value > 0:
            return value
        else:
            raise ValueError(f'{key} must be greater than 0')

    author = db.relationship('Author', back_populates='books')
    publisher = db.relationship('Publisher', back_populates='books')

    # serialize_rules = ('-author.books', '-publisher.books')

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "page_count": self.page_count,
            "publisher": self.publisher.to_dict_without_books()
        }


class Publisher(db.Model, SerializerMixin):
    __tablename__ = 'publishers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer, nullable=False, default=2000)

    @validates('founding_year')
    def validate_year(self, key, value):
        if 2023 >= value >= 1600:
            return value
        else:
            raise ValueError(f'{key} must be between 1600 and 2023')

    books = db.relationship('Book', back_populates='publisher')
    authors = association_proxy('books', 'author')

    serialize_rules = ('-books.publisher',)

    def to_dict_without_books(self):
        return {
            "id": self.id,
            "name": self.name,
            "founding_year": self.founding_year
        }


class Author(db.Model, SerializerMixin):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    pen_name = db.Column(db.String)

    books = db.relationship('Book', back_populates='author')
    publishers = association_proxy('books', 'publisher')

    serialize_rules = ('-books.author',)