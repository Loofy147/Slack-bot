"""
أمثلة على استخدام قدرات التكامل المباشر
"""

# مثال 1: إنشاء مشروع Flask جديد
FLASK_PROJECT_EXAMPLE = {
    "topic": "إنشاء تطبيق ويب بسيط باستخدام Flask",
    "integration_requests": [
        {
            "integration_request": {
                "type": "package_management",
                "parameters": {
                    "operation": "install",
                    "package": "flask"
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": "app.py",
                    "content": """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return {'message': 'Hello from Flask API!'}

if __name__ == '__main__':
    app.run(debug=True)
"""
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_directory",
                    "path": "templates"
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": "templates/index.html",
                    "content": """<!DOCTYPE html>
<html>
<head>
    <title>Flask App</title>
</head>
<body>
    <h1>مرحباً بك في تطبيق Flask!</h1>
    <button onclick="loadData()">تحميل البيانات</button>
    <div id="data"></div>
    
    <script>
        function loadData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('data').innerHTML = data.message;
                });
        }
    </script>
</body>
</html>
"""
                }
            }
        },
        {
            "integration_request": {
                "type": "environment_variables",
                "parameters": {
                    "operation": "set",
                    "key": "FLASK_ENV",
                    "value": "development"
                }
            }
        }
    ]
}

# مثال 2: إعداد قاعدة بيانات SQLite
DATABASE_SETUP_EXAMPLE = {
    "topic": "إعداد قاعدة بيانات للمستخدمين",
    "integration_requests": [
        {
            "integration_request": {
                "type": "package_management",
                "parameters": {
                    "operation": "install",
                    "package": "sqlite3"
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": "database.py",
                    "content": """import sqlite3
from datetime import datetime

class UserDatabase:
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, username, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email) VALUES (?, ?)',
                (username, email)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        conn.close()
        return users

if __name__ == '__main__':
    db = UserDatabase()
    print("تم إنشاء قاعدة البيانات بنجاح!")
"""
                }
            }
        },
        {
            "integration_request": {
                "type": "system_commands",
                "parameters": {
                    "command": "python database.py"
                }
            }
        }
    ]
}

# مثال 3: إعداد مشروع React
REACT_PROJECT_EXAMPLE = {
    "topic": "إنشاء تطبيق React جديد",
    "integration_requests": [
        {
            "integration_request": {
                "type": "system_commands",
                "parameters": {
                    "command": "npx create-react-app my-react-app"
                }
            }
        },
        {
            "integration_request": {
                "type": "system_commands",
                "parameters": {
                    "command": "npm install axios react-router-dom",
                    "working_dir": "my-react-app"
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": "my-react-app/src/components/UserList.js",
                    "content": """import React, { useState, useEffect } from 'react';
import axios from 'axios';

function UserList() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const response = await axios.get('/api/users');
            setUsers(response.data);
        } catch (error) {
            console.error('خطأ في تحميل المستخدمين:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div>جارٍ التحميل...</div>;
    }

    return (
        <div>
            <h2>قائمة المستخدمين</h2>
            <ul>
                {users.map(user => (
                    <li key={user.id}>
                        {user.username} - {user.email}
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default UserList;
"""
                }
            }
        }
    ]
}

# مثال 4: إعداد Docker
DOCKER_SETUP_EXAMPLE = {
    "topic": "إعداد Docker للمشروع",
    "integration_requests": [
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": "Dockerfile",
                    "content": """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
"""
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": "docker-compose.yml",
                    "content": """version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - .:/app
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": ".dockerignore",
                    "content": """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.venv
.env
"""
                }
            }
        }
    ]
}

# مثال 5: إعداد CI/CD مع GitHub Actions
GITHUB_ACTIONS_EXAMPLE = {
    "topic": "إعداد CI/CD مع GitHub Actions",
    "integration_requests": [
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_directory",
                    "path": ".github/workflows"
                }
            }
        },
        {
            "integration_request": {
                "type": "file_system",
                "parameters": {
                    "operation": "create_file",
                    "path": ".github/workflows/ci.yml",
                    "content": """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=./ --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to production
      run: |
        echo "نشر التطبيق في الإنتاج"
        # أوامر النشر هنا
"""
                }
            }
        }
    ]
}

def get_example_by_topic(topic_keyword):
    """الحصول على مثال حسب الموضوع"""
    examples = {
        'flask': FLASK_PROJECT_EXAMPLE,
        'database': DATABASE_SETUP_EXAMPLE,
        'react': REACT_PROJECT_EXAMPLE,
        'docker': DOCKER_SETUP_EXAMPLE,
        'github': GITHUB_ACTIONS_EXAMPLE
    }

    for key, example in examples.items():
        if key in topic_keyword.lower():
            return example

    return None


if __name__ == '__main__':
    print("أمثلة على استخدام قدرات التكامل المباشر:")
    print("1. Flask Project")
    print("2. Database Setup")
    print("3. React Project")
    print("4. Docker Setup")
    print("5. GitHub Actions")