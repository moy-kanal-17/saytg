import mysql.connector
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def connect_db():
    """Подключение к базе данных MySQL."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="moykanal17",
            database="users_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Ошибка подключения: {err}")
        return None

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    username = request.form['username']
    message = request.form['message']

    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO messages (username, message) VALUES (%s, %s)"
            cursor.execute(query, (username, message))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify(success=True)
        except mysql.connector.Error as err:
            print(f"Ошибка при сохранении сообщения: {err}")
            return jsonify(success=False, error="Ошибка базы данных")
    return jsonify(success=False, error="Ошибка подключения к базе данных")

@app.route('/load_messages', methods=['GET'])
def load_messages():
    connection = connect_db()
    if connection:
        try:
            cursor = connection.cursor()
            query = "SELECT username, message, timestamp FROM messages ORDER BY timestamp ASC"
            cursor.execute(query)
            messages = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify([
                {'username': msg[0], 'message': msg[1], 'timestamp': msg[2].strftime('%Y-%m-%d %H:%M:%S')} for msg in messages
            ])
        except mysql.connector.Error as err:
            print(f"Ошибка при загрузке сообщений: {err}")
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
