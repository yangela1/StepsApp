import os
from dotenv import load_dotenv
from datetime import timedelta
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import requests
# Load environment variables from .env file
load_dotenv()

# Retrieve the secret key from the environment
SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM") 
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
RESET_PASSWORD_EXPIRE_MINUTES = int(os.getenv("RESET_PASSWORD_EXPIRE_MINUTES"))
RESET_PASSWORD_SECRET_KEY = os.getenv("RESET_PASSWORD_SECRET_KEY")

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY") 
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN") 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks that entered password is same as hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Creates an access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_password_reset_token(email: str):
    """Generate a JWT token for password reset."""
    expire = datetime.utcnow() + timedelta(minutes=30)  # Token expiry time, adjust as needed
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, RESET_PASSWORD_SECRET_KEY, algorithm=ALGORITHM)
    return token

def send_reset_email(email: str, reset_link: str):
    """
    Sends a password reset email using Mailgun.
    """
    html_content = f"""
    <html>
        <body>
         <p>We received a request to reset your password. Please click the link below to reset your password:</p>
         <p><a href="{reset_link}" style="color: #0066cc; text-decoration: underline;">{reset_link}</a></p>
        </body>
    </html>
    """

    response = requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Your App <mailgun@{MAILGUN_DOMAIN}>",
            "to": email,
            "subject": "Password Reset Request",
            "html": html_content  
        }
    )
    return response