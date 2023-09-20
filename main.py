import requests
from datetime import datetime
from my_data import MY_POSITION
import time
import smtplib
from credentials import my_email, password, smtp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

my_lat = MY_POSITION[0]
my_lng = MY_POSITION[1]

def is_iss_close():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    if my_lat - 5  <= iss_longitude <= my_lat + 5 and my_lng -5 <= iss_latitude <= my_lng + 5:
        return True
    return False

def is_dark():
    parameters = {
        "lat": my_lat,
        "lng": my_lng,
        "formatted": 0,
    }

    # ------ Get Sunset and Sunrise time -------- #
    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise_h = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunrise_m = int(data["results"]["sunrise"].split("T")[1].split(":")[1])
    sunset_h = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    sunset_m = int(data["results"]["sunset"].split("T")[1].split(":")[1])

    time_now = datetime.now()
    hour_now = time_now.hour
    minute_now = time_now.minute
    # To test
    # hour_now = 20
    if hour_now < sunrise_h and minute_now < sunrise_m or hour_now > sunset_h and minute_now > sunset_m:
        return True
    return False

def send_email(email, msg):
    with smtplib.SMTP(smtp) as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)

        email_message = MIMEMultipart()
        email_message['Subject'] = 'ISS Overhead Notifier'
        email_message['From'] = my_email
        email_message['To'] = email

        text_body = MIMEText(msg, 'plain', 'utf-8')
        email_message.attach(text_body)

        connection.sendmail(
            from_addr=my_email, 
            to_addrs=email, 
            msg=email_message.as_string()
        )

while True:
    print('Starting...')
    if is_iss_close() and is_dark():
        send_email(
            email='andre.silva.rodrigues@gmail.com',
            msg='Pay close attention now! The ISS is above you!'
        )
    print('Ending...')
    time.sleep(60)
