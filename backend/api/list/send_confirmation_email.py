import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import FileResponse, RedirectResponse
import jwt
from db.get_db import get_db
from sqlalchemy.orm import Session
from db.models import List
from datetime import datetime, timedelta
from pathlib import Path

load_dotenv()

BACKEND_URL = os.getenv('BACKEND_URL')
FROM_EMAIL = os.getenv('FROM_EMAIL')
SUBJECT = os.getenv('SUBJECT')
SMTP = os.getenv('SMTP')
PASSWORD = os.getenv('PASSWORD')
MP3_FILE = os.getenv('MP3_FILE')
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

# Function to send confirmation email
def send_confirmation_email(to_email: str, referral_code: str):
    from_email = FROM_EMAIL

    # Create the body of the email
    body = f"""
    Please click the link below to confirm your email:
    {BACKEND_URL}/{referral_code}
    
    Once confirmed, you'll be able to download your exclusive MP3 file.
    
    P.S. If for some reason you lose your file (or there's a glitch), try requesting it here: {BACKEND_URL}/lost/{referral_code}
    """

    # Create the message
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'plain'))

    # Send the email via SMTP
    try:
        with smtplib.SMTP(SMTP, 587) as server:
            server.starttls()
            server.login(FROM_EMAIL, PASSWORD)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to generate a download token
def generate_download_token(referral_code: str, email: str, expiration_time: timedelta = timedelta(hours=1)) -> str:
    # Create the payload with referral_code, email, and expiration time
    payload = {
        "referral_code": referral_code,
        "email": email,
        "exp": datetime.utcnow() + expiration_time  # Use timedelta here
    }
    # Encode the payload into a JWT token
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Function to confirm email
def confirm_email(referral_code: str, db: Session = Depends(get_db)):
    # Find the user with the referral code
    user = db.query(List).filter(List.referral_code == referral_code).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid referral code")

    # Mark the user as confirmed
    user.confirmed = True
    db.commit()
    db.refresh(user)

    # Generate the download token for the user
    download_token = generate_download_token(referral_code=user.referral_code, email=user.email)

    # Redirect the user to the download page with the token
    download_url = f"{BACKEND_URL}/list/download/{download_token}"

    # Return the redirect response to the download URL
    return RedirectResponse(url=download_url)

# Function to download the file
# Function to download the file
def download_file(download_token: str, db: Session = Depends(get_db)):
    # Verify the token
    user = verify_download_token(download_token, db)

    # Check if the user is confirmed
    if not user.confirmed:
        raise HTTPException(status_code=400, detail="You need to confirm your email before downloading the file")

    # File path to download (assuming you have a static file)
    file_path = Path(MP3_FILE)

    # Check if the file exists
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # If the user hasn't downloaded the file yet, mark it as downloaded
    if not user.download_used:
        # Mark the download as used
        user.download_used = True
        db.commit()

    # Return the file for download with appropriate headers
    return FileResponse(file_path, media_type="audio/mpeg", filename="can_you_see_it.mp3")

# Function to verify the download token
def verify_download_token(download_token: str, db: Session) -> List:
    try:
        # Decode the token using the secret key
        payload = jwt.decode(download_token, SECRET_KEY, algorithms=["HS256"])

        # Extract referral_code and email from the token payload
        referral_code = payload.get("referral_code")
        email = payload.get("email")
        expiration = payload.get("exp")

        if not referral_code or not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        # Check if the token has expired
        if datetime.utcnow() > datetime.utcfromtimestamp(expiration):
            raise HTTPException(status_code=400, detail="The download link has expired")

        # Find the user associated with the referral code and email
        user = db.query(List).filter(List.referral_code == referral_code, List.email == email).first()

        if not user:
            raise HTTPException(status_code=400, detail="Invalid referral code or email")

        if user.download_used:
            raise HTTPException(status_code=400, detail="The download link has already been used")

        return user  # If the user is found and token is valid

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="The download link has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

# Function to re-enable file download for the user
def reset_download(user: List, db: Session):
    # Reset download_used to False to allow a new download
    user.download_used = False
    db.commit()
    db.refresh(user)

# Function to generate a new download token after the user requests it
def generate_new_download_token(referral_code: str, email: str, db: Session) -> str:
    # Find the user to verify
    user = db.query(List).filter(List.referral_code == referral_code, List.email == email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found or invalid details")
    
    # Ensure the user is confirmed before resetting the download flag
    if not user.confirmed:
        raise HTTPException(status_code=400, detail="Email is not confirmed")

    # Reset the download_used flag to allow a new download
    reset_download(user, db)
    
    # Generate a new download token
    download_token = generate_download_token(referral_code=user.referral_code, email=user.email)
    return download_token

# Function to send a new download link for lost files
def resend_link(referral_code: str, db: Session = Depends(get_db)):
    # Find the user with the referral code
    user = db.query(List).filter(List.referral_code == referral_code).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid referral code")

    # Ensure the user is confirmed
    if not user.confirmed:
        raise HTTPException(status_code=400, detail="You need to confirm your email before requesting the download link")

    # Generate a new download token for the user
    new_download_token = generate_new_download_token(referral_code=user.referral_code, email=user.email, db=db)

    # Send the new download token to the user's email (or return it directly)
    send_lost_file_email(user.email, new_download_token)

    return {"message": "New download link sent successfully"}

# Function to send the "lost file" download link email
def send_lost_file_email(to_email: str, download_token: str):
    from_email = FROM_EMAIL
    subject = "Your New Download Link"

    # Create the body of the email
    body = f"""
    It looks like you lost your file. Here is your new download link:
    {BACKEND_URL}/download/{download_token}
    
    If you have any issues, feel free to contact us.
    """

    # Create the message
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email via SMTP
    try:
        with smtplib.SMTP(SMTP, 587) as server:
            server.starttls()
            server.login(FROM_EMAIL, PASSWORD)
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
    except Exception as e:
        print(f"Failed to send email: {e}")
