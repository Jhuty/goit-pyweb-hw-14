from datetime import datetime, timedelta
from jose import JWTError, jwt
import smtplib
from email.mime.text import MIMEText



SECRET_KEY = "YSK"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception

def send_verification_email(user_email: str, verification_token: str):
    msg = MIMEText(f'Please verify your email by clicking on the following link: http://localhost:8000/verify/{verification_token}')
    msg['Subject'] = 'Email Verification'
    msg['From'] = 'your-email@example.com'
    msg['To'] = user_email

    with smtplib.SMTP('smtp.example.com') as server:
        server.login('your-email@example.com', 'your-email-password')
        server.send_message(msg)