"""
Demo Flask application with intentional bugs for testing Debuggle Core.
"""

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Demo user data
USERS = [
    {"id": 1, "name": "Alice", "email": "alice@demo.com", "role": "admin"},
    {"id": 2, "name": "Bob", "email": "bob@demo.com", "role": "user"}, 
    {"id": 3, "name": "Charlie", "email": "charlie@demo.com", "role": "user"}
]

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """Get user by ID - has potential IndexError bug."""
    # Bug: assumes user_id maps directly to list index
    user = USERS[user_id]  # IndexError if user_id >= len(USERS)
    return jsonify(user)

@app.route('/users/<int:user_id>/profile')
def get_user_profile(user_id):
    """Get user profile - has KeyError bug."""
    user = next((u for u in USERS if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Bug: assumes all users have 'profile' key
    profile_data = {
        "name": user["name"],
        "email": user["email"],
        "bio": user["profile"]["bio"],  # KeyError - 'profile' key doesn't exist
        "avatar": user["profile"]["avatar"]
    }
    
    return jsonify(profile_data)

@app.route('/calculate/<metric>')
def calculate_metric(metric):
    """Calculate metrics - has ZeroDivisionError bug."""
    
    # Demo data with some zeros
    metrics_data = {
        "success_rate": {"success": 95, "total": 100},
        "error_rate": {"errors": 5, "total": 100}, 
        "conversion": {"conversions": 0, "visits": 0},  # Division by zero potential
        "efficiency": {"completed": 80, "started": 100}
    }
    
    if metric not in metrics_data:
        return jsonify({"error": "Unknown metric"}), 400
    
    data = metrics_data[metric]
    
    if metric == "success_rate":
        rate = (data["success"] / data["total"]) * 100
    elif metric == "error_rate":
        rate = (data["errors"] / data["total"]) * 100
    elif metric == "conversion":
        rate = (data["conversions"] / data["visits"]) * 100  # ZeroDivisionError here!
    elif metric == "efficiency": 
        rate = (data["completed"] / data["started"]) * 100
    
    return jsonify({"metric": metric, "rate": f"{rate:.2f}%"})

@app.route('/process_data')
def process_data():
    """Process data - has TypeError bug."""
    
    # Mixed data types (realistic scenario)
    data_batch = [
        {"id": 1, "value": 100},
        {"id": 2, "value": 250},
        {"id": 3, "value": "invalid"},  # String instead of number
        {"id": 4, "value": 175}
    ]
    
    total = 0
    for item in data_batch:
        # Bug: assumes all values are numeric
        total += item["value"] * 1.5  # TypeError when value is string
    
    return jsonify({"total": total})

@app.route('/load_config')
def load_config():
    """Load configuration - has AttributeError bug."""
    
    class Config:
        def __init__(self):
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///demo.db")
            self.api_key = os.getenv("API_KEY", "default_key")
            # Missing get_secret_key method
    
    config = Config()
    
    # Bug: assumes config has get_secret_key method
    secret = config.get_secret_key()  # AttributeError - method doesn't exist
    
    return jsonify({
        "database": config.database_url,
        "api_key": config.api_key,
        "secret": secret
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)