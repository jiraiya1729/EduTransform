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