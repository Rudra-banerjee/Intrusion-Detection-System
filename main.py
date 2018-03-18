import RPi.GPIO as GPIO
import time
import picamera
import smtplib,imaplib
import os,email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
#from email.Utils import COMMSPACE,formatdate
from email import Encoders
GPIO.setmode(GPIO.BCM)
#sending mail from the pi to the user containing media
def send_mail(num):
    send_from="arghaberry@gmail.com"
    send_to="mayukhmajhi@gmail.com"
    subject="Home Surveillance"
    text="Intruder Detected"

    file1='image'+str(num)+'.jpg'
    try:
        os.rename('video'+str(num)+'.h264','video'+str(num)+'.mp4')
    except:
        pass
    file2="video"+str(num)+".mp4"
    file3='image'+str(num+1)+'.jpg'
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = subject
    
    msg.attach( MIMEText(text) )

    part1 = MIMEBase('application', "octet-stream")
    fo1=open(file1,"rb")
    part1.set_payload(fo1.read() )
    Encoders.encode_base64(part1)
    part1.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file1))
    msg.attach(part1)


    part2 = MIMEBase('application', "octet-stream")
    fo2=open(file2,"rb")
    part2.set_payload(fo2.read() )
    Encoders.encode_base64(part2)
    part2.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file2))
    msg.attach(part2)

    part3 = MIMEBase('application', "octet-stream")
    fo3=open(file3,"rb")
    part3.set_payload(fo3.read() )
    Encoders.encode_base64(part3)
    part3.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file3))
    msg.attach(part3) 

    smtp = smtplib.SMTP("smtp.gmail.com",587) 
    smtp.ehlo()
    smtp.starttls()  
    smtp.login("arghaberry@gmail.com","nitd@12345") 
    sent=smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
    

#Shooting Video and capturing image from the Pi camera
def picamerause(num):
    camera=picamera.PiCamera()
    camera.capture('image'+str(num)+'.jpg')
    time.sleep(1)
    camera.start_recording('video'+str(num)+'.h264')
    time.sleep(5)
    camera.stop_recording()
    time.sleep(1)
    camera.capture('image'+str(num+1)+'.jpg')
    camera.close()

#reading email 
def read_email_from_gmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('arghaberry@gmail.com','nitd@12345')
    

    while True:
        mail.select('inbox')
        type, data = mail.search(None, 'UnSeen')
        mail_ids = data[0]
        id_list = mail_ids.split()   

        try:
            latest_email_id = int(id_list[-1])
            typ, data = mail.fetch(latest_email_id, '(RFC822)' )
            raw_email=data[0][1]
                    
            email_message = email.message_from_string(raw_email)
                     
            sender= email.utils.parseaddr(email_message['From']) # for parsing "Yuji Tomita" <yuji@grovemade.com>
            sub= email_message['Subject'] 

            if sender[1]=='arghasen10@gmail.com' or sender[1]=='mayukhmajhi@gmail.com' and sub=='Open':
                print('Gate opened')
                GPIO.output(red,False)
                GPIO.output(yellow,False)
                GPIO.output(green,True)
                time.sleep(10)
            mail.store(data[0].replace(' ',','),'+FLAGS','\Seen')
        except IndexError:
            pass
        except AttributeError:
            GPIO.output(red,True)
            GPIO.output(yellow,False)
            GPIO.output(green,False)
            print('Gate Closed')
            break
    
# use Raspberry Pi board pin numbers


# set GPIO Pins
pinTrigger = 18
pinEcho = 24
yellow=17
green=27
red=22

# set GPIO input and output channels
GPIO.setup(pinTrigger, GPIO.OUT)
GPIO.setup(pinEcho, GPIO.IN)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(yellow,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)

num=0

while True:
        num=num+1
	# set Trigger to HIGH
	GPIO.output(pinTrigger, True)
	# set Trigger after 0.01ms to LOW
	time.sleep(0.00001)
	GPIO.output(pinTrigger, False)
        GPIO.output(red,True)
        GPIO.output(yellow,False)
        GPIO.output(green,False)

	startTime = time.time()
	stopTime = time.time()

	# save start time
	while 0 == GPIO.input(pinEcho):
		startTime = time.time()

	# save time of arrival
	while 1 == GPIO.input(pinEcho):
		stopTime = time.time()

	# time difference between start and arrival
	TimeElapsed = stopTime - startTime
	# multiply with the sonic speed (34300 cm/s)
	# and divide by 2, because there and back
	distance = (TimeElapsed * 34300) / 2

	print ("Distance: %.1f cm" % distance)
	if (distance<=60):
            print('Capturing video and Photo of Intruder...')
            GPIO.output(yellow,True)
            GPIO.output(red,False)
            GPIO.output(green,False)
            picamerause(num)
            print("Sending Mail......")
            send_mail(num)
            print("Waiting for User's command...")
            read_email_from_gmail()
	time.sleep(1)
GPIO.setwarnings(False)
GPIO.cleanup()