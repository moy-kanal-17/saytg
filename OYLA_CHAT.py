import mysql.connector
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QLineEdit, QTextEdit, QMessageBox, QFileDialog, QPushButton
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont  # Import QFont to change font properties

class Chat(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.setWindowTitle(name)
        self.vbox = QVBoxLayout()
        
        self.chat_box = QTextEdit()
        self.chat_box.setEnabled(False)
        self.chat_box.setFontPointSize(14)  # Set the font size for chat messages

        self.input = QLineEdit()
        self.input.setFont(QFont("Arial", 14))  # Set font size for input text
        self.btn_send = QPushButton("Send", clicked=self.send_message)
        self.btn_image = QPushButton("Send Image", clicked=self.send_image)
        self.btn_clear = QPushButton("Clear Chat", clicked=self.clear_chat)  # Button to clear chat
        
        self.vbox.addWidget(self.chat_box)
        self.vbox.addWidget(self.input)
        self.vbox.addWidget(self.btn_send)
        self.vbox.addWidget(self.btn_image)
        self.vbox.addWidget(self.btn_clear)  # Add clear button to the layout
        
        self.setStyleSheet("""
            QWidget {
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 0.5, 
                    fx: 0.5, fy: 0.5,
                    stop: 0 rgba(0, 99, 255, 1),
                    stop: 0.36 rgba(7, 7, 7, 1),
                    stop: 0.38 rgba(0, 140, 255, 1)
                );
                color: white;  /* Optional: Set text color for better visibility */
            }
        """)
        self.setLayout(self.vbox)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(3)  # Timer will trigger every 3 seconds

        self.show()

    def send_message(self):
        """Function to send a message in the chat and save it to the database."""
        message = self.input.text()  # Get the message text
        username = self.name  # Use the user's name as the sender

        if message:
            # Display message in the app's chat
            self.chat_box.append(f"{username}: {message}")

            # Save message to the database
            connection = self.connect_db()
            if connection:
                try:
                    cursor = connection.cursor()
                    query = "INSERT INTO messages (username, message) VALUES (%s, %s)"
                    cursor.execute(query, (username, message))
                    connection.commit()
                    cursor.close()
                    connection.close()
                    self.input.clear()  # Clear input field after sending
                except mysql.connector.Error as err:
                    print(f"Error saving message: {err}")
            else:
                print("Database connection error.")
        else:
            QMessageBox.warning(self, "Error", "Enter a message before sending.")

    def send_image(self):
        """Function to send an image in the chat."""
        # Open a file dialog to select an image
        image_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            username = self.name
            self.chat_box.append(f"{username}: <img src='{image_path}' width='200'>")

            # Store image message in the database (optional)
            connection = self.connect_db()
            if connection:
                try:
                    cursor = connection.cursor()
                    query = "INSERT INTO messages (username, message) VALUES (%s, %s)"
                    cursor.execute(query, (username, f"<img src='{image_path}' width='200'>"))
                    connection.commit()
                    cursor.close()
                    connection.close()
                except mysql.connector.Error as err:
                    print(f"Error saving image message: {err}")

    def load_chat_messages(self):
        """Load and display chat messages from the database."""
        connection = self.connect_db()

        if connection:
            try:
                cursor = connection.cursor()
                query = "SELECT username, message, timestamp FROM messages ORDER BY timestamp ASC"
                cursor.execute(query)

                messages = cursor.fetchall()
                cursor.close()
                connection.close()

                # Display messages in the chat
                self.chat_box.clear()  # Clear before loading new messages
                for message in messages:
                    self.chat_box.append(f"{message[0]} ({message[2]}): {message[1]}")

            except mysql.connector.Error as err:
                print(f"Error loading messages: {err}")
        else:
            print("Database connection error.")

    def refresh(self):
        """Method to refresh the chat, triggered by the timer."""
        self.load_chat_messages()

    def clear_chat(self):
        """Method to clear the chat box and delete all messages from the database."""
        self.chat_box.clear()  # Clear the chat display
        connection = self.connect_db()
        if connection:
            try:
                cursor = connection.cursor()
                # Permanently delete all messages from the database
                cursor.execute("DELETE FROM messages")
                connection.commit()
                cursor.close()
                connection.close()
                QMessageBox.information(self, "Success", "Chat has been cleared and all messages have been deleted.")
            except mysql.connector.Error as err:
                print(f"Error clearing messages: {err}")

    def connect_db(self):
        """Function to connect to the MySQL database."""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="moykanal17",
                database="users_db"
            )
            return connection
        except mysql.connector.Error as err:
            print(f"Connection error: {err}")
            return None


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.users = []
        self.name = QLineEdit()
        self.name.setPlaceholderText("Enter your name..")
        self.name.setFont(QFont("Arial", 14))  # Set font size for name input
        self.btn = QPushButton("Join", clicked=self.join)
        self.setStyleSheet("""  # Set background for the window
            QWidget {
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 0.5, 
                    fx: 0.5, fy: 0.5,
                    stop: 0 rgba(0, 99, 255, 1),
                    stop: 0.36 rgba(7, 7, 7, 1),
                    stop: 0.38 rgba(0, 140, 255, 1)
                );
                color: white;  /* Optional: Set text color for better visibility */
            }
        """)
        self.layout.addWidget(self.name)
        self.layout.addWidget(self.btn)
        self.setLayout(self.layout)
        self.show()
    
    def join(self):
        chat = Chat(self.name.text())
        self.users.append(chat)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    user_management_app = Window()
    user_management_app.show()  
    sys.exit(app.exec_())
