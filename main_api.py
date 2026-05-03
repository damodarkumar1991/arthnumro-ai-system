from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
from io import BytesIO
import os
import re
import jwt
import bcrypt

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ── Supabase client (REST via supabase-py) ──
from supabase import create_client, Client

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')  # service_role key
JWT_SECRET   = os.environ.get('JWT_SECRET', 'arthnumro-secret-change-in-prod')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────

def generate_token(user_id: str, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=72),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def get_current_user():
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None, 'Missing token'
    token = auth.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload.get('user_id')
        result  = supabase.table('users').select('*').eq('id', user_id).single().execute()
        if not result.data:
            return None, 'User not found'
        return result.data, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired — please log in again'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'
    except Exception as e:
        return None, str(e)


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, error = get_current_user()
        if error:
            return jsonify({'error': error}), 401
        return f(user, *args, **kwargs)
    return decorated


def calculate_life_path(dob_str: str) -> dict:
    """Accept DD/MM/YYYY or YYYY-MM-DD"""
    try:
        if '/' in dob_str:
            parts = dob_str.split('/')
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            date_obj = datetime.strptime(dob_str, '%Y-%m-%d')
            d, m, y = date_obj.day, date_obj.month, date_obj.year

        digits = [int(x) for x in f"{d:02d}{m:02d}{y}"]
        total  = sum(digits)
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(x) for x in str(total))

        meanings = {
            1:  "The Leader — Independent, pioneering, and ambitious",
            2:  "The Peacemaker — Diplomatic, sensitive, and cooperative",
            3:  "The Creative — Expressive, optimistic, and social",
            4:  "The Builder — Practical, disciplined, and hardworking",
            5:  "The Freedom Seeker — Adventurous, versatile, and dynamic",
            6:  "The Nurturer — Responsible, caring, and harmonious",
            7:  "The Seeker — Analytical, spiritual, and introspective",
            8:  "The Powerhouse — Ambitious, successful, and authoritative",
            9:  "The Humanitarian — Compassionate, generous, and idealistic",
            11: "The Visionary — Intuitive, inspired, and enlightened",
            22: "The Master Builder — Practical visionary, turns dreams into reality",
            33: "The Master Teacher — Compassionate leader, spiritual guide"
        }
        return {'number': total, 'meaning': meanings.get(total, 'The Path Seeker')}
    except Exception as e:
        return {'error': str(e)}


# ────────────────────────────────────────────────────────────
# HEALTH
# ────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'service':   'Arthnumro AI',
        'status':    'healthy',
        'timestamp': datetime.now().isoformat()
    })


# ────────────────────────────────────────────────────────────
# AUTH: REGISTER
# ────────────────────────────────────────────────────────────

@app.route('/register', methods=['POST'])
def register():
    try:
        data     = request.json or {}
        name     = (data.get('name')     or '').strip()
        email    = (data.get('email')    or '').strip().lower()
        password = (data.get('password') or '')
        dob      = (data.get('dob')      or '').strip()

        if not name or not email or not password:
            return jsonify({'error': 'Name, email and password are required'}), 400
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # Check duplicate
        existing = supabase.table('users').select('id').eq('email', email).execute()
        if existing.data:
            return jsonify({'error': 'An account with this email already exists'}), 409

        # Hash password
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Calculate life path
        life_path_num = None
        if dob:
            lp = calculate_life_path(dob)
            if 'number' in lp:
                life_path_num = lp['number']

        # Parse DOB to date format for DB
        birth_date_db = None
        if dob and '/' in dob:
            try:
                parts = dob.split('/')
                birth_date_db = f"{parts[2]}-{parts[1]:>02}-{parts[0]:>02}"
            except Exception:
                pass

        # Insert user
        insert_data = {
            'name':          name,
            'email':         email,
            'password_hash': pw_hash,
            'dob':           dob,
            'birth_date':    birth_date_db,
            'life_path':     life_path_num,
            'token_balance': 5,
            'subscription_status': 'free'
        }
        result = supabase.table('users').insert(insert_data).execute()
        user   = result.data[0]

        token = generate_token(user['id'], email)
        print(f"✅ Registered: {email}")

        return jsonify({
            'success': True,
            'token':   token,
            'user': {
                'name':           user['name'],
                'email':          email,
                'dob':            dob,
                'life_path':      life_path_num,
                'questions_left': user['token_balance']
            }
        }), 201

    except Exception as e:
        import traceback
        print(f"Register error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ────────────────────────────────────────────────────────────
# AUTH: LOGIN
# ────────────────────────────────────────────────────────────

@app.route('/login', methods=['POST'])
def login():
    try:
        data     = request.json or {}
        email    = (data.get('email')    or '').strip().lower()
        password = (data.get('password') or '')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        result = supabase.table('users').select('*').eq('email', email).execute()
        if not result.data:
            return jsonify({'error': 'Invalid email or password'}), 401

        user = result.data[0]
        if not user.get('password_hash'):
            return jsonify({'error': 'Account setup incomplete — please register again'}), 401

        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401

        token = generate_token(user['id'], email)
        print(f"✅ Login: {email}")

        return jsonify({
            'success': True,
            'token':   token,
            'user': {
                'name':           user['name'],
                'email':          email,
                'dob':            user.get('dob', ''),
                'life_path':      user.get('life_path'),
                'questions_left': user.get('token_balance', 0)
            }
        })

    except Exception as e:
        import traceback
        print(f"Login error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ────────────────────────────────────────────────────────────
# CHAT — authenticated, saves messages to Supabase
# ────────────────────────────────────────────────────────────

@app.route('/chat', methods=['POST'])
@require_auth
def chat(current_user):
    try:
        import anthropic

        data         = request.json or {}
        messages_in  = data.get('messages', [])
        user_context = data.get('user_context', {})

        if not messages_in:
            return jsonify({'error': 'No messages provided'}), 400

        # Check token balance
        tokens_left = current_user.get('token_balance', 0)
        if tokens_left <= 0:
            return jsonify({
                'error': 'No questions remaining. Please purchase more tokens.',
                'upgrade_required': True
            }), 402

        # User context
        name      = user_context.get('name')      or current_user.get('name', 'friend')
        dob       = user_context.get('dob')       or current_user.get('dob', '')
        life_path = user_context.get('life_path') or current_user.get('life_path', 'unknown')

        # Calculate age
        age = 'unknown'
        if dob:
            try:
                if '/' in dob:
                    parts = dob.split('/')
                    birth_obj = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                else:
                    birth_obj = datetime.strptime(dob, '%Y-%m-%d')
                today = datetime.now()
                age = today.year - birth_obj.year - (
                    (today.month, today.day) < (birth_obj.month, birth_obj.day)
                )
            except Exception:
                pass

        system_prompt = f"""You are Arthnumro AI — a warm, wise, and deeply intuitive numerology guide with 20 years of experience.

You are speaking with {name}.

THEIR NUMEROLOGY PROFILE:
- Life Path Number: {life_path}
- Date of Birth: {dob}
- Age: {age}
- Current Year: {datetime.now().year}

YOUR STYLE:
- Warm, encouraging, and specific — never generic
- Use {name}'s name 2-3 times per response
- Give exact timing: "March–April 2026", not "soon"
- Include lucky numbers, colours, gemstones where relevant
- End every response with one engaging follow-up question
- Keep responses under 220 words — concise but packed with insight
- Use light formatting (bold for key points) but no excessive markdown

ALWAYS provide:
1. A direct, specific answer to their question
2. One concrete action they can take today
3. A follow-up question to deepen the reading"""

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not configured'}), 500

        client = anthropic.Anthropic(api_key=api_key)

        claude_messages = [
            {'role': m['role'], 'content': m['content']}
            for m in messages_in
            if m.get('role') in ('user', 'assistant') and m.get('content')
        ]

        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=400,
            system=system_prompt,
            messages=claude_messages
        )

        reply = response.content[0].text

        # ── Save messages to Supabase ──
        user_id = current_user['id']
        last_user_msg = next(
            (m for m in reversed(messages_in) if m.get('role') == 'user'), None
        )
        if last_user_msg:
            supabase.table('messages').insert({
                'user_id':    user_id,
                'role':       'user',
                'content':    last_user_msg['content'],
                'tokens_used': 0
            }).execute()

        supabase.table('messages').insert({
            'user_id':    user_id,
            'role':       'assistant',
            'content':    reply,
            'tokens_used': 1
        }).execute()

        # ── Deduct token balance ──
        new_balance = max(0, tokens_left - 1)
        supabase.table('users').update(
            {'token_balance': new_balance}
        ).eq('id', user_id).execute()

        print(f"✅ Chat: {current_user['email']} | balance: {new_balance}")

        return jsonify({
            'success':        True,
            'reply':          reply,
            'questions_left': new_balance
        })

    except Exception as e:
        import traceback
        print(f"Chat error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ────────────────────────────────────────────────────────────
# ME — get current user info
# ────────────────────────────────────────────────────────────

@app.route('/me', methods=['GET'])
@require_auth
def get_me(current_user):
    return jsonify({
        'success': True,
        'user': {
            'name':           current_user.get('name'),
            'email':          current_user.get('email'),
            'dob':            current_user.get('dob'),
            'life_path':      current_user.get('life_path'),
            'questions_left': current_user.get('token_balance', 0)
        }
    })


# ────────────────────────────────────────────────────────────
# EXISTING ENDPOINTS BELOW — keep everything as-is
# ────────────────────────────────────────────────────────────

def calculate_life_path_original(birthdate):
    """Original endpoint helper — kept for backward compat"""
    try:
        date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
        date_str = date_obj.strftime('%Y%m%d')
        total = sum(int(digit) for digit in date_str)
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(digit) for digit in str(total))
        meanings = {
            1: "The Leader - Independent, pioneering, and ambitious",
            2: "The Peacemaker - Diplomatic, sensitive, and cooperative",
            3: "The Creative - Expressive, optimistic, and social",
            4: "The Builder - Practical, disciplined, and hardworking",
            5: "The Freedom Seeker - Adventurous, versatile, and dynamic",
            6: "The Nurturer - Responsible, caring, and harmonious",
            7: "The Seeker - Analytical, spiritual, and introspective",
            8: "The Powerhouse - Ambitious, successful, and authoritative",
            9: "The Humanitarian - Compassionate, generous, and idealistic",
            11: "The Visionary - Intuitive, inspired, and enlightened",
            22: "The Master Builder - Practical visionary, turns dreams into reality",
            33: "The Master Teacher - Compassionate leader, spiritual guide"
        }
        return {'number': total, 'meaning': meanings.get(total, "Unknown")}
    except Exception as e:
        return {'error': str(e)}


leads_db = {}


@app.route('/api/calculate/life-path', methods=['POST'])
def calculate_life_path_endpoint():
    try:
        data      = request.json
        birthdate = data.get('birthdate')
        name      = data.get('name')
        email     = data.get('email')
        if not birthdate:
            return jsonify({'error': 'Birthdate is required'}), 400
        result = calculate_life_path_original(birthdate)
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        lead_id = None
        if email:
            lead_id = f"lead_{datetime.now().timestamp()}"
            leads_db[lead_id] = {
                'id': lead_id, 'email': email, 'name': name,
                'birthdate': birthdate, 'life_path': result['number'],
                'created_at': datetime.now().isoformat()
            }
        return jsonify({
            'success': True,
            'life_path': result['number'],
            'meaning': result['meaning'],
            'lead_id': lead_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leads', methods=['GET'])
def get_leads():
    return jsonify({'success': True, 'leads': list(leads_db.values()), 'total': len(leads_db)})


@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Legacy chat endpoint — kept for backward compat"""
    try:
        import anthropic
        data       = request.json
        message    = data.get('message')
        user_data  = data.get('user_data', {})
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not configured'}), 500
        client = anthropic.Anthropic(api_key=api_key)
        name       = user_data.get('name', 'friend')
        life_path  = user_data.get('life_path', 'unknown')
        birth_date = user_data.get('birth_date', 'unknown')
        system_prompt = f"""You are an expert numerologist giving specific, actionable insights to {name}.
Life Path: {life_path} | Birth: {birth_date} | Current year: {datetime.now().year}
Be warm, specific, and always end with a follow-up question. Under 200 words."""
        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=400,
            system=system_prompt,
            messages=[{'role': 'user', 'content': message}]
        )
        return jsonify({
            'success':  True,
            'response': response.content[0].text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
