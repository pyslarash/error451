from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from argon2 import PasswordHasher

Base = declarative_base()

### To update the models do this:
# alembic revision --autogenerate
# alembic upgrade head

# Password hasher setup
ph = PasswordHasher()

class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    two_factor = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)

    @validates('password_hash')
    def validate_password(self, key, password):
        """Hash the password before saving it."""
        return ph.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify the given password."""
        try:
            print(f"Verifying password: {password}")  # Debugging line to check the input password
            print(f"Stored hash: {self.password_hash}")  # Debugging line to check the stored password hash
            return ph.verify(self.password_hash, password)
        except Exception as e:
            print(f"Error verifying password: {e}")  # Debugging line to see any error
            return False


class List(Base):
    __tablename__ = 'list'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    confirmed = Column(Boolean, default=False)
    subscribed = Column(Boolean, default=True)
    referral_code = Column(String, unique=True, nullable=False)
    country_code = Column(String(2), nullable=False)
    city = Column(String, nullable=False)
    state_code = Column(String(2))
    zip = Column(String)
    download_used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<List(name={self.name}, email={self.email}, confirmed={self.confirmed})>"

class Config(Base):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)

class BlacklistedToken(Base):
    __tablename__ = 'blacklisted_tokens'
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)