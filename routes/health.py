from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and CI/CD"""
    return jsonify({
        'status': 'UP',
        'service': 'Aeterna Flask',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

