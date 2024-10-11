#### FacialRecognitionChatbot
This is python code that performs facial recognition before unlocking a chatbot feature. It takes feature encodings from a detected face and compares it to the ones stored in the registered user directory.

To implement this in Python, a few packages need to be installed:

- cv2 (OpenCV): Used for capturing and processing video frames for facial recognition.
- threading: Allows concurrent execution of facial recognition and chatbot tasks.
- speech_recognition: Converts spoken input from the microphone into text using Google’s Web Speech API.
- google.generativeai: Powers the AI chatbot that generates conversational responses.
- pyttsx3: Converts chatbot text responses into audible speech.
- face_recognition: Detects and verifies user faces from webcam footage.
- tkinter: Provides the graphical user interface for the chatbot and video display.
- scrolledtext: Displays chatbot conversation in a scrollable text box.
- PIL (Pillow): Converts webcam images into a format suitable for display in the GUI.
- os: Handles loading images from the file system for facial recognition.

  You'll also need to have a Gemini API for response generation and your own pictures in the image directory so that it can recognize your face.
