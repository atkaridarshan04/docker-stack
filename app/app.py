import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")


_secret_path = os.environ.get('MYSQL_PASSWORD_FILE')
if _secret_path and os.path.exists(_secret_path):
    with open(_secret_path) as f:
        app.config['MYSQL_PASSWORD'] = f.read().strip()
    logger.info("MySQL password loaded from secret file.")
else:
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
    logger.warning("MySQL password loaded from environment variable.")

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'admin')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'mydb')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
PrometheusMetrics(app)


def _query(sql, args=None, commit=False):
    """Execute a query, always closing the cursor."""
    cur = mysql.connection.cursor()
    try:
        cur.execute(sql, args or [])
        if commit:
            mysql.connection.commit()
            return cur.lastrowid
        return cur.fetchall()
    finally:
        cur.close()


@app.route('/')
def index():
    rows = _query('SELECT id, message FROM messages')
    messages = [(r['id'], r['message']) for r in rows]
    return render_template('index.html', messages=messages)


@app.route('/submit', methods=['POST'])
def submit():
    msg = request.form.get('new_message', '').strip()
    if not msg:
        return jsonify({'error': 'Message required'}), 400
    message_id = _query('INSERT INTO messages (message) VALUES (%s)', [msg], commit=True)
    return jsonify({'message': msg, 'id': message_id})


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    _query('DELETE FROM messages WHERE id = %s', [id], commit=True)
    return jsonify({'status': 'deleted'})


@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    content = request.form.get('updated_message', '').strip()
    if not content:
        return jsonify({'error': 'New message required'}), 400
    _query('UPDATE messages SET message = %s WHERE id = %s', (content, id), commit=True)
    return jsonify({'status': 'updated', 'message': content})


@app.route('/health')
def health():
    try:
        _query('SELECT 1')
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
