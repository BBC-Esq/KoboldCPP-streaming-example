import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import QThread, Signal
import requests
import sseclient
import logging

import download_kobold

class APIWorker(QThread):
    token_received = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, url, payload):
        super().__init__()
        self.url = url
        self.payload = payload

    def run(self):
        try:
            response = requests.post(self.url, json=self.payload, stream=True)
            response.raise_for_status()
            client = sseclient.SSEClient(response)
            for event in client.events():
                if event.event == "message":
                    try:
                        data = json.loads(event.data)
                        if 'token' in data:
                            self.token_received.emit(data['token'])
                        else:
                            logging.warning(f"Unexpected data format: {data}")
                    except json.JSONDecodeError:
                        logging.error(f"Failed to parse JSON: {event.data}")
                        self.error_occurred.emit(f"Failed to parse: {event.data}")
                else:
                    logging.info(f"Received non-message event: {event.event}")
        except Exception as e:
            logging.error(f"Error in API request: {str(e)}")
            self.error_occurred.emit(str(e))

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat with KoboldAI")
        self.setGeometry(100, 100, 1100, 600)

        layout = QVBoxLayout()

        self.system_message_label = QLabel()
        self.system_message_label.setWordWrap(True)
        layout.addWidget(self.system_message_label)

        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        layout.addWidget(self.response_area, stretch=1)

        input_layout = QHBoxLayout()

        # Add the download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.show_download_window)
        input_layout.addWidget(self.download_button)

        self.input_area = QLineEdit()
        self.input_area.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_area)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)
        self.connected = True

        # KoboldAI API endpoint
        self.api_url = "http://localhost:5001/api/extra/generate/stream"
        self.current_response = ""

        def send_message(self):
            prompt = self.input_area.text()
            self.input_area.clear()
            self.current_response = ""
            
            self.response_area.clear()
            
            self.response_area.append(f"<b>You:</b> {prompt}")
            self.response_area.append("\n")
            self.get_completion(prompt)

    def get_completion(self, prompt):
        payload = {
            "prompt": prompt,
            "max_context_length": 4096,
            "max_length": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            # "rep_pen": 1.0,
            # "rep_pen_range": 2048,
            # "rep_pen_slope": 0.7,
            # "tfs": 0.97,
            # "top_a": 0.8,
            # "top_k": 0,
            # "typical": 0.19,
        }

        self.worker = APIWorker(self.api_url, payload)
        self.worker.token_received.connect(self.update_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def update_response(self, token):
        self.current_response += token
        cursor_position = self.response_area.textCursor().position()
        self.response_area.moveCursor(QTextCursor.End)
        self.response_area.insertPlainText(token)
        cursor = self.response_area.textCursor()
        cursor.setPosition(cursor_position)
        self.response_area.setTextCursor(cursor)
        QApplication.processEvents()

    def handle_error(self, error_message):
        self.response_area.append(f"<b>Error:</b> {error_message}")

    def show_system_message(self, message):
        self.system_message_label.setText(message)
        self.system_message_label.adjustSize()

    def show_download_window(self):
        try:
            download_window = download_kobold.DownloadWindow()
            download_window.show()
            self.download_window = download_window
            print("Download window opened successfully")
        except Exception as e:
            print(f"Error opening download window: {str(e)}")
            self.show_system_message(f"Error opening download window: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())