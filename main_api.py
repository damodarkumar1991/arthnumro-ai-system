from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
import os
import jwt
import bcrypt
import hmac
import hashlib
import time
import requests as req_lib
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ── Supabase ─────────────────────────────────────────────────
from supabase import create_client, Client

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
JWT_SECRET   = os.environ.get('JWT_SECRET', 'arthnumro-secret-change-in-prod')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Razorpay config (no package needed) ──────────────────────
RZP_KEY_ID         = os.environ.get('RAZORPAY_KEY_ID', '')
RZP_KEY_SECRET     = os.environ.get('RAZORPAY_KEY_SECRET', '')
RZP_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', '')

# ── Question packs ────────────────────────────────────────────
PACKS = {
    'starter':  {'questions': 5,  'amount_paise': 19900, 'label': 'Starter'},
    'explorer': {'questions': 20, 'amount_paise': 49900, 'label': 'Explorer'},
    'seeker':   {'questions': 50, 'amount_paise': 99900, 'label': 'Seeker'},
}


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def generate_token(user_id: str, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email':   email,
        'exp':     datetime.utcnow() + timedelta(hours=72),
        'iat':     datetime.utcnow()
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
    try:
        if '/' in dob_str:
            parts = dob_str.split('/')
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            date_obj = datetime.strptime(dob_str, '%Y-%m-%d')
            d, m, y  = date_obj.day, date_obj.month, date_obj.year
        digits = [int(x) for x in f"{d:02d}{m:02d}{y}"]
        total  = sum(digits)
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(x) for x in str(total))
        meanings = {
            1:  'The Leader — Independent, pioneering, and ambitious',
            2:  'The Peacemaker — Diplomatic, sensitive, and cooperative',
            3:  'The Creative — Expressive, optimistic, and social',
            4:  'The Builder — Practical, disciplined, and hardworking',
            5:  'The Freedom Seeker — Adventurous, versatile, and dynamic',
            6:  'The Nurturer — Responsible, caring, and harmonious',
            7:  'The Seeker — Analytical, spiritual, and introspective',
            8:  'The Powerhouse — Ambitious, successful, and authoritative',
            9:  'The Humanitarian — Compassionate, generous, and idealistic',
            11: 'The Visionary — Intuitive, inspired, and enlightened',
            22: 'The Master Builder — Practical visionary, turns dreams into reality',
            33: 'The Master Teacher — Compassionate leader, spiritual guide'
        }
        return {'number': total, 'meaning': meanings.get(total, 'The Path Seeker')}
    except Exception as e:
        return {'error': str(e)}


# ─────────────────────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'service':   'Arthnumro AI',
        'status':    'healthy',
        'timestamp': datetime.now().isoformat()
    })


# ─────────────────────────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────────────────────────

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

        existing = supabase.table('users').select('id').eq('email', email).execute()
        if existing.data:
            return jsonify({'error': 'An account with this email already exists'}), 409

        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        life_path_num = None
        if dob:
            lp = calculate_life_path(dob)
            if 'number' in lp:
                life_path_num = lp['number']

        birth_date_db = None
        if dob and '/' in dob:
            try:
                parts = dob.split('/')
                birth_date_db = f"{parts[2]}-{int(parts[1]):02d}-{int(parts[0]):02d}"
            except Exception:
                pass

        result = supabase.table('users').insert({
            'name':                 name,
            'email':                email,
            'password_hash':        pw_hash,
            'dob':                  dob,
            'birth_date':           birth_date_db,
            'life_path':            life_path_num,
            'questions_left':       5,
            'total_questions_used': 0,
            'subscription_status':  'free'
        }).execute()

        user  = result.data[0]
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
                'questions_left': 5
            }
        }), 201

    except Exception as e:
        import traceback
        print(f"Register error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────

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
            return jsonify({'error': 'Account setup incomplete'}), 401

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
                'questions_left': user.get('questions_left', 0)
            }
        })

    except Exception as e:
        import traceback
        print(f"Login error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# ME
# ─────────────────────────────────────────────────────────────

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
            'questions_left': current_user.get('questions_left', 0)
        }
    })


# ─────────────────────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────────────────────

@app.route('/chat', methods=['POST'])
@require_auth
def chat(current_user):
    try:
        import anthropic

        data        = request.json or {}
        messages_in = data.get('messages', [])
        user_context = data.get('user_context', {})

        if not messages_in:
            return jsonify({'error': 'No messages provided'}), 400

        questions_left = current_user.get('questions_left', 0)
        if questions_left <= 0:
            return jsonify({
                'error': 'No questions remaining. Please purchase more.',
                'upgrade_required': True,
                'packs': {k: {'questions': v['questions'],
                              'amount_rupees': v['amount_paise'] // 100}
                          for k, v in PACKS.items()}
            }), 402

        name      = user_context.get('name')      or current_user.get('name', 'friend')
        dob       = user_context.get('dob')       or current_user.get('dob', '')
        life_path = user_context.get('life_path') or current_user.get('life_path', 'unknown')

        personal_year = 'unknown'
        age = 'unknown'
        if dob:
            try:
                if '/' in dob:
                    parts     = dob.split('/')
                    birth_obj = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
                else:
                    birth_obj = datetime.strptime(dob, '%Y-%m-%d')
                today = datetime.now()
                age   = today.year - birth_obj.year - (
                    (today.month, today.day) < (birth_obj.month, birth_obj.day)
                )
                personal_year = (birth_obj.day + birth_obj.month + today.year) % 9 or 9
            except Exception:
                pass

        system_prompt = f"""You are Arthnumro AI — a warm, wise numerology guide blending Vedic and Pythagorean traditions.

User: {name} | DOB: {dob} | Age: {age} | Life Path: {life_path} | Personal Year: {personal_year} | Year: {datetime.now().year}

Style: warm and specific, use their name 2-3 times, give exact timing windows, include lucky numbers/colours where relevant, end with one follow-up question, keep under 220 words."""

        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not configured'}), 500

        client = anthropic.Anthropic(api_key=api_key)
        claude_messages = [
            {'role': m['role'], 'content': m['content']}
            for m in messages_in
            if m.get('role') in ('user', 'assistant') and m.get('content')
        ]

        start_ms = int(time.time() * 1000)
        response = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=400,
            system=system_prompt,
            messages=claude_messages
        )
        elapsed_ms  = int(time.time() * 1000) - start_ms
        reply       = response.content[0].text
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        user_id       = current_user['id']
        new_q_left    = max(0, questions_left - 1)
        user_question = next(
            (m['content'] for m in reversed(messages_in) if m.get('role') == 'user'), ''
        )

        # Decrement questions_left atomically
        supabase.rpc('decrement_questions', {'p_user_id': user_id}).execute()

        # Update last_active
        supabase.table('users').update({
            'last_active':          datetime.utcnow().isoformat(),
            'total_questions_used': current_user.get('total_questions_used', 0) + 1,
        }).eq('id', user_id).execute()

        # Log to questions_log
        supabase.table('questions_log').insert({
            'user_id':              user_id,
            'question':             user_question,
            'response':             reply,
            'life_path':            life_path if isinstance(life_path, int) else None,
            'personal_year':        personal_year if isinstance(personal_year, int) else None,
            'questions_left_after': new_q_left,
            'tokens_used':          tokens_used,
            'response_ms':          elapsed_ms,
        }).execute()

        # Also save to messages table
        if user_question:
            supabase.table('messages').insert({
                'user_id': user_id, 'role': 'user',
                'content': user_question, 'tokens_used': 0
            }).execute()
        supabase.table('messages').insert({
            'user_id': user_id, 'role': 'assistant',
            'content': reply, 'tokens_used': 1
        }).execute()

        print(f"✅ Chat: {current_user['email']} | questions_left: {new_q_left}")

        return jsonify({
            'success':        True,
            'reply':          reply,
            'questions_left': new_q_left
        })

    except Exception as e:
        import traceback
        print(f"Chat error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# PAYMENT: CREATE ORDER
# ─────────────────────────────────────────────────────────────

@app.route('/payment/create-order', methods=['POST'])
@require_auth
def create_order(current_user):
    try:
        data     = request.json or {}
        pack_key = data.get('pack', '')

        if pack_key not in PACKS:
            return jsonify({'error': 'Invalid pack. Choose starter, explorer or seeker'}), 400

        pack = PACKS[pack_key]

        # Call Razorpay API directly — no package needed
        rzp_resp = req_lib.post(
            'https://api.razorpay.com/v1/orders',
            auth=HTTPBasicAuth(RZP_KEY_ID, RZP_KEY_SECRET),
            json={
                'amount':   pack['amount_paise'],
                'currency': 'INR',
                'receipt':  f"an_{current_user['id'][:8]}_{int(time.time())}",
                'notes': {
                    'user_id':    current_user['id'],
                    'user_email': current_user['email'],
                    'pack':       pack_key,
                }
            }
        )

        if rzp_resp.status_code != 200:
            print(f"Razorpay error: {rzp_resp.text}")
            return jsonify({'error': 'Payment gateway error. Try again.'}), 502

        rzp_order = rzp_resp.json()

        supabase.table('purchases').insert({
            'user_id':             current_user['id'],
            'pack_name':           pack_key,
            'questions_purchased': pack['questions'],
            'amount_paise':        pack['amount_paise'],
            'razorpay_order_id':   rzp_order['id'],
            'payment_status':      'created',
        }).execute()

        print(f"✅ Order created: {rzp_order['id']} | {current_user['email']} | {pack_key}")

        return jsonify({
            'order_id':   rzp_order['id'],
            'amount':     pack['amount_paise'],
            'currency':   'INR',
            'key_id':     RZP_KEY_ID,
            'pack_label': pack['label'],
            'questions':  pack['questions'],
        })

    except Exception as e:
        import traceback
        print(f"Create order error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# PAYMENT: WEBHOOK
# ─────────────────────────────────────────────────────────────

@app.route('/payment/webhook', methods=['POST'])
def razorpay_webhook():
    try:
        received_sig = request.headers.get('X-Razorpay-Signature', '')
        body_bytes   = request.get_data()

        expected_sig = hmac.new(
            RZP_WEBHOOK_SECRET.encode('utf-8'),
            body_bytes,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig, received_sig):
            print('❌ Webhook signature mismatch')
            return jsonify({'error': 'Invalid signature'}), 400

        event = request.json or {}
        if event.get('event') != 'payment.captured':
            return jsonify({'status': 'ignored'}), 200

        payment  = event['payload']['payment']['entity']
        order_id = payment.get('order_id')
        pay_id   = payment.get('id')

        result = supabase.table('purchases').select('*').eq(
            'razorpay_order_id', order_id
        ).single().execute()

        if not result.data:
            print(f'❌ Webhook: order not found {order_id}')
            return jsonify({'error': 'Order not found'}), 404

        purchase = result.data

        if purchase.get('questions_credited'):
            return jsonify({'status': 'already_credited'}), 200

        user_id   = purchase['user_id']
        questions = purchase['questions_purchased']

        supabase.rpc('increment_questions', {
            'p_user_id':   user_id,
            'p_increment': questions
        }).execute()

        supabase.table('purchases').update({
            'payment_status':      'paid',
            'razorpay_payment_id': pay_id,
            'razorpay_signature':  received_sig,
            'questions_credited':  True,
            'paid_at':             datetime.utcnow().isoformat(),
        }).eq('id', purchase['id']).execute()

        print(f"✅ Payment captured: {pay_id} | user: {user_id} | +{questions} questions")
        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        import traceback
        print(f"Webhook error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# LEGACY ENDPOINTS — backward compatibility
# ─────────────────────────────────────────────────────────────

def calculate_life_path_original(birthdate):
    try:
        date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
        date_str = date_obj.strftime('%Y%m%d')
        total    = sum(int(d) for d in date_str)
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(d) for d in str(total))
        meanings = {
            1: 'The Leader', 2: 'The Peacemaker', 3: 'The Creative',
            4: 'The Builder', 5: 'The Freedom Seeker', 6: 'The Nurturer',
            7: 'The Seeker', 8: 'The Powerhouse', 9: 'The Humanitarian',
            11: 'The Visionary', 22: 'The Master Builder', 33: 'The Master Teacher'
        }
        return {'number': total, 'meaning': meanings.get(total, 'Unknown')}
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
            'success': True, 'life_path': result['number'],
            'meaning': result['meaning'], 'lead_id': lead_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leads', methods=['GET'])
def get_leads():
    return jsonify({'success': True, 'leads': list(leads_db.values()), 'total': len(leads_db)})


@app.route('/api/chat/message', methods=['POST'])
def chat_message():
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
Life Path: {life_path} | Birth: {birth_date} | Year: {datetime.now().year}
Be warm, specific, always end with a follow-up question. Under 200 words."""
        response = client.messages.create(
            model='claude-sonnet-4-20250514', max_tokens=400,
            system=system_prompt,
            messages=[{'role': 'user', 'content': message}]
        )
        return jsonify({'success': True, 'response': response.content[0].text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
