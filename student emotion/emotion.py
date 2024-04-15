import cv2
import tensorflow as tf
import numpy as np

class EmotionDetector:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_emotions(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

        emotions_data = []

        for (x, y, w, h) in faces:
            face_roi = gray_frame[y:y + h, x:x + w]
            face_roi = cv2.resize(face_roi, (48, 48))
            face_roi = np.expand_dims(face_roi, axis=0)
            face_roi = face_roi / 255.0  # Normalize pixel values
            face_roi = np.reshape(face_roi, (1, 48, 48, 1))

            emotion_probabilities = self.model.predict(face_roi)
            predicted_emotion = self.emotion_labels[np.argmax(emotion_probabilities)]

            emotions_data.append({'label': predicted_emotion, 'box': [x, y, w, h]})

        return emotions_data

from opencv import VideoProcessor

def main():
    video_path = "data/classroom/video1.mp4"
    model_path = "model/inbuilt/emotion_model.h5"
    output_path = "output/video_output6.mp4"
    save_interval = 1

    video_processor = VideoProcessor(video_path, model_path, output_path, save_interval)
    video_processor.process_video()

if __name__ == "__main__":
    main()
