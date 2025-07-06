from flask import Blueprint, json, request, jsonify, render_template, current_app
from datetime import datetime
from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

def extract_webhook_data(payload):
    """Extract relevant data from GitHub webhook payload"""
    action_type = None
    author = None
    from_branch = None
    to_branch = None
    request_id = None
    timestamp = datetime.utcnow().isoformat() + 'Z'

    if 'commits' in payload and payload.get('ref'):
        action_type = 'PUSH'
        author = payload.get('pusher', {}).get('name') or payload.get('sender', {}).get('login')
        to_branch = payload.get('ref', '').replace('refs/heads/', '')
        from_branch = to_branch 
        request_id = payload.get('head_commit', {}).get('id', '')[:7] 

    elif 'pull_request' in payload:
        pull_request = payload['pull_request']
        action_type = 'PULL_REQUEST'
        author = pull_request.get('user', {}).get('login')
        from_branch = pull_request.get('head', {}).get('ref')
        to_branch = pull_request.get('base', {}).get('ref')
        request_id = str(pull_request.get('id'))

        if payload.get('action') == 'closed' and pull_request.get('merged'):
            action_type = 'MERGE'
            author = pull_request.get('merged_by', {}).get('login') or author
    
    return {
        'request_id': request_id,
        'author': author,
        'action': action_type,
        'from_branch': from_branch,
        'to_branch': to_branch,
        'timestamp': timestamp
    }

@webhook.route('/receiver', methods=["POST"])
def receiver():
    """GitHub webhook receiver endpoint"""
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No payload received'}), 400

        webhook_data = extract_webhook_data(payload)
        print(f"Extracted webhook data: {webhook_data}")

        if webhook_data['action'] and webhook_data['author']:
            result = mongo.db.webhook_events.insert_one(webhook_data)
            print(f"Insert result: {result.inserted_id}")
            
            print(f"Stored webhook event: {webhook_data['action']} by {webhook_data['author']}")
            
            return jsonify({
                'status': 'success',
                'message': 'Webhook processed successfully',
                'data': webhook_data
            }), 200
        else:
            print(f"Invalid webhook data - action: {webhook_data['action']}, author: {webhook_data['author']}")
            return jsonify({'error': 'Unable to process webhook data'}), 400
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal server error'}), 500

@webhook.route('/events', methods=["GET"])
def get_events():
    """API endpoint to get recent webhook events"""
    try:
        events = list(mongo.db.webhook_events.find(
            {}, 
            {'_id': 0}
        ).sort('timestamp', -1).limit(50))
        
        return jsonify({
            'status': 'success',
            'events': events
        }), 200
        
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@webhook.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
