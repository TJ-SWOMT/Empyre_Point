from flask import Flask, request, jsonify
from flask_cors import CORS
from services.user_accounts_service import UserAccountsService
from services.presentations_service import PresentationsService
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize services
user_service = UserAccountsService()
presentations_service = PresentationsService()

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        logger.debug(f"Received registration data: {data}")
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Create user
        user = user_service.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        return jsonify({
            'success': True,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Verify credentials
        user = user_service.verify_password(
            username=data['username'],
            password=data['password']
        )
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/presentations', methods=['POST'])
def create_presentation():
    print("create_presentation!!!!")
    try:
        data = request.get_json()
        print("data!!!!!!!!!!", data)
        logger.debug(f"Received presentation creation data: {data}")
        
        # Validate required fields
        required_fields = ['user_id', 'title']
        missing_fields = [field for field in required_fields if field not in data]
        # if missing_fields:
        #     error_msg = f'Missing required fields: {", ".join(missing_fields)}'
        #     logger.error(error_msg)
        #     return jsonify({'error': error_msg}), 400
        print("missing_fields", data)
        # Create presentation
        presentation = presentations_service.create_presentation(
            user_id=data['user_id'],
            title=data['title'],
            description=data.get('description')
        )
        
        return jsonify({
            'success': True,
            'presentation': presentation
        }), 201
        
    except Exception as e:
        logger.error(f"Presentation creation error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/presentations/<presentation_id>', methods=['GET'])
def get_presentation(presentation_id):
    try:
        presentation = presentations_service.get_presentation(presentation_id)
        if presentation:
            return jsonify({
                'success': True,
                'presentation': presentation
            }), 200
        else:
            return jsonify({'error': 'Presentation not found'}), 404
            
    except Exception as e:
        logger.error(f"Error retrieving presentation: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/user/<int:user_id>/presentations', methods=['GET'])
def get_user_presentations(user_id):
    try:
        print("get_user_presentations!!!!33333")
        presentations = presentations_service.get_user_presentations(user_id)
        print("presentations", presentations)
        
        if presentations:
            return jsonify({
                'success': True,
                'presentations': presentations
            }), 200
        else:
            return jsonify({
                'success': True,
                'presentations': None
            }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving user presentations: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/presentations/<presentation_id>', methods=['PUT'])
def update_presentation(presentation_id):
    try:
        data = request.get_json()
        if not data or not any(key in data for key in ['title', 'description']):
            return jsonify({'error': 'At least one field (title or description) must be provided'}), 400
        
        presentation = presentations_service.update_presentation(
            presentation_id=presentation_id,
            title=data.get('title'),
            description=data.get('description')
        )
        
        if presentation:
            return jsonify({
                'success': True,
                'presentation': presentation
            }), 200
        else:
            return jsonify({'error': 'Presentation not found'}), 404
            
    except Exception as e:
        logger.error(f"Error updating presentation: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/presentations/<presentation_id>', methods=['DELETE'])
def delete_presentation(presentation_id):
    try:
        success = presentations_service.delete_presentation(presentation_id)
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Presentation not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting presentation: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/presentations/<presentation_id>/slides', methods=['POST'])
def create_slide(presentation_id):
    try:
        data = request.get_json()
        logger.debug(f"Received slide creation data: {data}")
        
        # Validate required fields
        if 'slide_number' not in data:
            return jsonify({'error': 'Missing required field: slide_number'}), 400
        
        # Create slide
        slide = presentations_service.create_slide(
            presentation_id=presentation_id,
            slide_number=data['slide_number'],
            background_color=data.get('background_color', '#FFFFFF'),
            background_image_url=data.get('background_image_url')
        )
        
        return jsonify({
            'success': True,
            'slide': slide
        }), 201
        
    except Exception as e:
        logger.error(f"Slide creation error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/slides/<slide_id>', methods=['PUT'])
def update_slide(slide_id):
    try:
        data = request.get_json()
        if not data or not any(key in data for key in ['slide_number', 'background_color', 'background_image_url']):
            return jsonify({'error': 'At least one field must be provided for update'}), 400
        
        slide = presentations_service.update_slide(
            slide_id=slide_id,
            slide_number=data.get('slide_number'),
            background_color=data.get('background_color'),
            background_image_url=data.get('background_image_url')
        )
        
        if slide:
            return jsonify({
                'success': True,
                'slide': slide
            }), 200
        else:
            return jsonify({'error': 'Slide not found'}), 404
            
    except Exception as e:
        logger.error(f"Error updating slide: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/slides/<slide_id>', methods=['DELETE'])
def delete_slide(slide_id):
    try:
        success = presentations_service.delete_slide(slide_id)
        if success:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Slide not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting slide: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 