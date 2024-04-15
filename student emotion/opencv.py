import cv2
from emotion import EmotionDetector
import time
import csv
import pandas as pd

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class VideoProcessor:
    def __init__(self, video_path, model_path, output_path, save_interval=10):
        self.video_path = video_path
        self.output_path = output_path
        self.emotion_detector = EmotionDetector(model_path)
        self.save_interval = save_interval

    def process_video(self):
        cap = cv2.VideoCapture(self.video_path)

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        fps = int(cap.get(5))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (frame_width, frame_height))

        cv2.namedWindow("Emotion Detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Emotion Detection", 300, 400)
        emotions_data = []

        start_time = None
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1
            if frame_count == 15:  # Processed 15 frames
                frame_count = 0
                emotions_data = self.emotion_detector.detect_emotions(frame)

                out.write(frame)

                cv2.imshow("Emotion Detection", frame)

                if start_time is None:
                    start_time = time.time()

                elapsed_time = time.time() - start_time
                if elapsed_time >= self.save_interval:
                    self.save_emotions_to_csv(emotions_data)
                    self.evaluate('emotionsvideo1.csv')
                    start_time = None

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                time.sleep(2)  # Wait for 2 seconds before processing the next set of frames

        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def save_emotions_to_csv(self, emotions_data):
        with open('emotionsvideo1.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Label', 'Box'])
            for emotion_data in emotions_data:
                writer.writerow([emotion_data['label'], emotion_data['box']])

    def evaluate(self,path):
        df=pd.read_csv("emotionsvideo1.csv")
        df=df.drop(columns=['Box'])
        df = df[df['Label'] != 'Label']
        label_counts = df['Label'].value_counts()
        # print(label_counts)
        total_count = label_counts.sum()
        Interest_Index = ((0.6* label_counts['Happy']) + (0.3*label_counts['Neutral']) - (0.1 * label_counts['Sad']))/total_count
        print(Interest_Index)
        if Interest_Index < 0.3:
            self.sendNotification()


    def sendNotification(self):


        # Email configuration
        email_sender = 'vjcreatinai@gmail.com'
        email_receiver = 'gaddiabhinav@gmail.com'
        email_subject = 'Notification'
        email_body = 'Engage the students.'

        # SMTP server configuration (Gmail example)
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587  # Gmail's SMTP port

        # Login credentials (make sure to enable less secure apps access or use app password)
        smtp_username = 'vjcreatinai@gmail.com'
        smtp_password = 'mlqi iiep sygj qidr'

        # Create email message
        message = MIMEMultipart()
        message['From'] = email_sender
        message['To'] = email_receiver
        message['Subject'] = email_subject
        message.attach(MIMEText(email_body, 'plain'))

        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(smtp_username, smtp_password)

        # Send email
        server.sendmail(email_sender, email_receiver, message.as_string())

        # Close connection
        server.quit()

        print("Notification email sent successfully.")