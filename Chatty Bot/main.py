import cv2
import threading
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
import face_recognition
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import os

engine = pyttsx3.init()

# Configure your Gemini API key
API_KEY = '(your api key here)'
genai.configure(api_key=API_KEY)

# Initialize text-to-speech engine
def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to recognize speech from the microphone
def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
    
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }
    
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"
    
    return response

# Function to interact with the Gemini chatbot
def chat_with_gemini(input_text):
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    response = chat.send_message(input_text)
    return response.text

# Function to perform facial recognition and handle chatbot interaction
def recognize_face_and_chat(gui):
    cap = cv2.VideoCapture(0)
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    registered_user_image = None
    known_face_encodings = []

    # Load the registered user's images and perform facial recognition
    image_paths = [os.path.join('labelled_images', f) for f in os.listdir('labelled_images')]
    for image_path in image_paths:
        img = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(img)
        if encoding:
            known_face_encodings.append(encoding[0])
            if registered_user_image is None:  # Check if it's None
                registered_user_image = img

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            current_face_locations = face_recognition.face_locations(rgb_frame)
            current_face_encodings = face_recognition.face_encodings(rgb_frame, current_face_locations)

            matches = []
            for encoding in current_face_encodings:
                match = face_recognition.compare_faces(known_face_encodings, encoding)
                if True in match:
                    matches.append(True)

            if any(matches):
                gui.update_chat("Registered user detected. System unlocked.")
                speak_text("Hello! I am Chatty Bot. How can I help you today?")
                # Capture and process speech input
                response = recognize_speech_from_mic(recognizer, microphone)
                gui.update_chat("Response loading . .")
                if response["transcription"]:
                    chatbot_response = chat_with_gemini(response['transcription'])
                    gui.update_chat("Response loaded.")
                    speak_text(chatbot_response)
                else:
                    gui.update_chat(f"Error: {response['error']}")
            else:
                gui.update_chat("Unregistered user detected. Access denied.")
                
        except Exception as e:
            print(f"Error analyzing frame: {e}")
            
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        
        gui.update_video(imgtk)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# GUI class
class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatty Bot")
        self.root.geometry("800x680")
        self.root.configure(bg='#2E2E2E')  # Dark grey background

        self.video_frame = tk.Label(root, width=800, height=400, bg='#2E2E2E', bd=0)
        self.video_frame.grid(column=0, row=0, padx=10, pady=10)
        self.video_frame.configure(highlightthickness=2, highlightbackground="white", highlightcolor="white")

        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=10, bg='#2E2E2E', fg='white', bd=0)
        self.chat_display.grid(column=0, row=1, padx=10, pady=10)
        self.chat_display.config(state=tk.DISABLED, font=("Helvetica", 12))

        self.quit_button = tk.Button(root, text="Quit", command=root.quit, bg='#2E2E2E', fg='white', bd=0)
        self.quit_button.grid(column=0, row=2, padx=10, pady=10)
        self.quit_button.configure(font=("Helvetica", 12, "bold"), highlightthickness=2, highlightbackground="white", highlightcolor="white")

        # Apply curved border-radius using an image overlay (workaround)
        self.round_corners(self.video_frame)
        self.round_corners(self.quit_button)

    def update_chat(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)  # Clear the chat display
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state=tk.DISABLED)

    def update_video(self, imgtk):
        self.video_frame.imgtk = imgtk
        self.video_frame.configure(image=imgtk)

    def round_corners(self, widget):
        widget.config(highlightbackground='#2E2E2E')  # Match the background color to remove visible border

def main():
    root = tk.Tk()
    gui = ChatbotGUI(root)

    # Start facial recognition and chatbot interaction in a separate thread
    face_and_chat_thread = threading.Thread(target=recognize_face_and_chat, args=(gui,))
    face_and_chat_thread.daemon = True
    face_and_chat_thread.start()

    root.mainloop()

if __name__ == "__main__":
    main()
 
