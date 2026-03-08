from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

def reduce_to_single_digit(number):
    """Reduce number to single digit, keeping master numbers 11, 22, 33"""
    master_numbers = {11, 22, 33}
    
    if number in master_numbers:
        return number
    
    while number > 9:
        number = sum(int(digit) for digit in str(number))
        if number in master_numbers:
            return number
    
    return number

def calculate_life_path(birthdate_str):
    """Calculate Life Path number from birthdate"""
    try:
        # Parse date (accepts YYYY-MM-DD format)
        date_obj = datetime.strptime(birthdate_str, '%Y-%m-%d')
        
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year
        
        # Reduce each component
        day_reduced = reduce_to_single_digit(day)
        month_reduced = reduce_to_single_digit(month)
        year_reduced = reduce_to_single_digit(year)
        
        # Sum and reduce
        total = day_reduced + month_reduced + year_reduced
        life_path = reduce_to_single_digit(total)
        
        return {
            'number': life_path,
            'calculation': f"{day} → {day_reduced}, {month} → {month_reduced}, {year} → {year_reduced}",
            'breakdown': {
                'day': day_reduced,
                'month': month_reduced,
                'year': year_reduced
            }
        }
    except Exception as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD: {str(e)}")

# Interpretations for each Life Path number
LIFE_PATH_MEANINGS = {
    1: "You're a natural leader with strong independence. Your path is about pioneering new ideas and standing confidently in your own power.",
    2: "You're a peacemaker and diplomat. Your path involves creating harmony, building partnerships, and using your intuitive nature to help others.",
    3: "You're a creative communicator. Your path is about self-expression, bringing joy to others, and sharing your unique talents with the world.",
    4: "You're a practical builder. Your path involves creating stable foundations, working methodically, and turning dreams into concrete reality.",
    5: "You're an adventurous free spirit. Your path is about embracing change, seeking experiences, and living life to its fullest.",
    6: "You're a nurturer and caregiver. Your path involves serving others, creating harmony in relationships, and being a pillar of your community.",
    7: "You're a seeker of truth. Your path is about spiritual growth, analyzing life's mysteries, and developing your inner wisdom.",
    8: "You're a natural achiever. Your path involves mastering the material world, building success, and using power responsibly.",
    9: "You're a humanitarian. Your path is about compassion, letting go, and making the world a better place for all.",
    11: "You're a spiritual messenger (Master Number). Your path involves inspiring others, developing intuition, and being a beacon of light.",
    22: "You're a master builder (Master Number). Your path involves turning grand visions into reality and leaving a lasting legacy.",
    33: "You're a master teacher (Master Number). Your path is about uplifting humanity through loving service and spiritual guidance."
}

# Store leads in memory (in production, use a database)
leads_db = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Arthnumro AI Automation'})

@app.route('/api/calculate/life-path', methods=['POST'])
def api_calculate_life_path():
    """Calculate Life Path number"""
    try:
        data = request.json
        birthdate = data.get('birthdate')
        email = data.get('email')
        name = data.get('name')
        
        if not birthdate:
            return jsonify({'error': 'Birthdate is required'}), 400
        
        result = calculate_life_path(birthdate)
        result['meaning'] = LIFE_PATH_MEANINGS.get(result['number'], '')
        
        # Store lead if email provided
        if email:
            lead_id = f"lead_{datetime.now().timestamp()}"
            leads_db[lead_id] = {
                'id': lead_id,
                'email': email,
                'name': name,
                'birthdate': birthdate,
                'life_path': result['number'],
                'created_at': datetime.now().isoformat()
            }
            result['lead_id'] = lead_id
        
        return jsonify({'success': True, 'data': result})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all captured leads"""
    return jsonify({
        'success': True,
        'count': len(leads_db),
        'leads': list(leads_db.values())
    })

if __name__ == '__main__':
    print("🚀 Starting Arthnumro AI Automation Server...")
    print("📍 Health Check: http://localhost:5000/health")
    print("📍 Calculate Life Path: POST http://localhost:5000/api/calculate/life-path")
    print("📍 View Leads: http://localhost:5000/api/leads")
    print("\n✨ Server is running! Keep this window open.\n")
    app.run(debug=True, host='0.0.0.0', port=8000)
