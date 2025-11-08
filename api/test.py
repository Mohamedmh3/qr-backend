"""
Simple test endpoint to verify Vercel Python runtime
"""

def handler(request):
    """Simple test handler"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': '{"status": "ok", "message": "Vercel Python runtime working"}'
    }

# For testing
app = handler
