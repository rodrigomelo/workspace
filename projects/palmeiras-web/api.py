"""
Palmeiras Web Dashboard - Vercel Server (Test)
"""
import json

def handler(event, context):
    """Test handler"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'status': 'ok', 'message': 'API is working'})
    }
