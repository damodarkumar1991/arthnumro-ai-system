from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os
from io import BytesIO
import re

app = Flask(__name__)
CORS(app)

# In-memory storage (in production, use a database)
leads_db = {}

def calculate_life_path(birthdate):
    """Calculate Life Path number from birthdate"""
    try:
        # Parse date
        date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
        
        # Sum all digits in the date
        date_str = date_obj.strftime('%Y%m%d')
        total = sum(int(digit) for digit in date_str)
        
        # Reduce to single digit (except 11, 22, 33)
        while total > 9 and total not in [11, 22, 33]:
            total = sum(int(digit) for digit in str(total))
        
        # Life Path meanings
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
        
        return {
            'number': total,
            'meaning': meanings.get(total, "Unknown")
        }
    except Exception as e:
        return {'error': str(e)}


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'service': 'Arthnumro AI Automation',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/calculate/life-path', methods=['POST'])
def calculate_life_path_endpoint():
    """Calculate Life Path number from birthdate"""
    try:
        data = request.json
        birthdate = data.get('birthdate')
        name = data.get('name')
        email = data.get('email')
        
        if not birthdate:
            return jsonify({'error': 'Birthdate is required'}), 400
        
        result = calculate_life_path(birthdate)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # Store lead
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
        
        return jsonify({
            'success': True,
            'life_path': result['number'],
            'meaning': result['meaning'],
            'lead_id': lead_id if email else None
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all captured leads"""
    return jsonify({
        'success': True,
        'leads': list(leads_db.values()),
        'total': len(leads_db)
    })


@app.route('/api/reports/generate-full', methods=['POST'])
def generate_full_report():
    """Generate complete AI-powered numerology report"""
    try:
        import anthropic
        
        data = request.json
        name = data.get('name')
        birthdate = data.get('birthdate')
        email = data.get('email')
        
        if not name or not birthdate:
            return jsonify({'error': 'Name and birthdate required'}), 400
        
        # Calculate Life Path number
        life_path_result = calculate_life_path(birthdate)
        life_path = life_path_result['number']
        
        # Initialize Claude
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key not configured'}), 500
            
        client = anthropic.Anthropic(api_key=api_key)
        
        # Generate ultra-comprehensive AI report
        current_year = datetime.now().year
        birth_date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
        age = current_year - birth_date_obj.year
        birth_month = birth_date_obj.month
        birth_day = birth_date_obj.day
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10000,
            messages=[{
                "role": "user",
                "content": f"""You are a master numerologist, past life regression therapist, and energy healer with 30 years of experience.

Create the most comprehensive, transformational numerology analysis ever written for:
- Name: {name}
- Life Path Number: {life_path}
- Birth Date: {birth_month}/{birth_day}/{birth_date_obj.year}
- Current Age: {age}
- Current Year: {current_year}

This is a PREMIUM $47 report. Make it life-changing, deeply personal, and incredibly valuable.

# THE COMPLETE LIFE BLUEPRINT FOR {name}

## EXECUTIVE SUMMARY
Write 3-4 paragraphs summarizing {name}'s:
- Soul essence and divine purpose
- Most important message they need right now
- The transformation available to them
- What makes their journey unique

---

## PART 1: CORE IDENTITY & LIFE PATH {life_path}

### Your Soul's Blueprint
Write 5-6 paragraphs exploring:
- The profound meaning of Life Path {life_path} for {name}
- Why their soul chose this path before incarnating
- How they're different from other Life Path {life_path}s
- The hero's journey they're on
- Their role in the collective evolution

### Natural Strengths & Superpowers
Detail 12-15 specific gifts with:
- How each gift manifests for {name}
- Real-world applications and examples
- How to amplify each strength
- Shadow side when misused
- Spiritual significance of each gift

### Life Lessons & Soul Contracts
Identify 7-9 major lessons including:
- Core karma to resolve
- Soul contracts with others
- How to recognize when in the lesson
- Specific practices to move through it
- Gifts received after mastering each lesson
- Timeline: when each lesson typically activates

---

## PART 2: PAST LIFE KARMA & SOUL HISTORY

### Past Life Influences on Life Path {life_path}
Based on Life Path {life_path} vibration, explore 4-5 past life themes:
- Ancient civilizations or time periods where {name} likely lived
- Roles they played (healer, warrior, teacher, ruler, mystic, etc.)
- Unfinished business brought into this lifetime
- Talents carried forward from past lives
- Old wounds still healing

### Karmic Debts & Soul Agreements
Detail:
- Karmic debt numbers from {birth_day} and {birth_month}
- What these debts mean for {name}
- People in their life who are soul contracts (by relationship type)
- How to resolve karma in this lifetime
- Signs that karma is clearing

### Past Life Gifts Activated Now
Identify 5-7 abilities {name} mastered in past lives:
- Specific skills that come "naturally"
- When these abilities first showed up in this life
- How to fully activate these dormant gifts
- Practices to remember past life wisdom

### Soul Age & Evolution Level
- Assess soul maturity based on Life Path {life_path}
- Current stage of spiritual evolution
- What this lifetime is preparing them for
- Next level of soul development

---

## PART 3: CHAKRA ALIGNMENT & ENERGY SYSTEM

### Numerology-Chakra Connection for Life Path {life_path}

For each chakra, based on Life Path {life_path}:

**ROOT CHAKRA (Survival, Safety, Grounding)**
- How Life Path {life_path} affects root chakra
- Likely imbalances for {name}
- Physical symptoms to watch for
- Healing practices and crystals
- Affirmations for root chakra balance

**SACRAL CHAKRA (Creativity, Sexuality, Emotions)**
- Creative expression aligned with {life_path}
- Emotional patterns unique to Life Path {life_path}
- Balancing practices
- Best creative outlets for {name}

**SOLAR PLEXUS (Power, Will, Confidence)**
- Personal power themes for Life Path {life_path}
- Where {name} gives power away
- How to reclaim sovereignty
- Confidence-building practices

**HEART CHAKRA (Love, Compassion, Connection)**
- Love language of Life Path {life_path}
- Heart opening/closing patterns
- Healing old heart wounds
- Practices for heart expansion

**THROAT CHAKRA (Truth, Expression, Communication)**
- How {name} should express their truth
- Communication style aligned with {life_path}
- Blocks to authentic expression
- Voice activation practices

**THIRD EYE (Intuition, Vision, Insight)**
- Psychic abilities of Life Path {life_path}
- How {name}'s intuition speaks to them
- Developing clairvoyance
- Meditation practices

**CROWN CHAKRA (Spirituality, Connection to Divine)**
- Spiritual gifts of Life Path {life_path}
- {name}'s unique connection to Source
- Mystical experiences to expect
- Enlightenment path

### Energy System Balancing Protocol
- Daily practice specifically for Life Path {life_path}
- Crystals and stones for {name}
- Essential oils and frequencies
- Foods that support their vibration
- Colors to wear and surround themselves with

---

## PART 4: LUCKY DATES & DIVINE TIMING

### Your Personal Power Dates for {current_year}-2050

**Monthly Power Days**
For Life Path {life_path}, identify:
- Best days each month for major decisions
- Days to avoid big commitments
- Lucky days for: money, love, career, spirituality

**Critical Life Timing Windows**

**For {current_year}:**
- Best months for: career moves, relationship decisions, investments, travel, starting new projects
- Days of maximum power/luck
- Challenging periods to navigate carefully

**Milestone Years {current_year}-2050:**
Highlight and explain these critical years:
- Personal Year 1 cycles (new beginnings)
- Personal Year 5 cycles (major change)
- Personal Year 9 cycles (completion/release)
- Ages: {age + 3}, {age + 7}, {age + 9}, {age + 11}, {age + 18}, {age + 27}

**Best Years for Major Life Events:**
Identify optimal timing for:
- Marriage/commitment
- Career change/launch
- Relocation/travel
- Major investment
- Spiritual awakening
- Retirement planning

---

## PART 5: BUSINESS & ENTREPRENEURSHIP GUIDANCE

### Should {name} Be in Business?
Based on Life Path {life_path}:
- Entrepreneurial potential score (1-10)
- Natural business strengths
- Business challenges to prepare for
- Best business models for their energy

### Business Name Numerology

**Creating a Powerful Business Name:**
Explain how to create a business name:
- Name vibration calculations
- Power numbers for business (1, 5, 8)
- Numbers to avoid (4, 7)
- 10 sample business name ideas with numerology calculations
- Which name vibration is most powerful for {name}

### Business Launch Timing
Best periods in {current_year} and {current_year + 1} to:
- Register business
- Launch website/product
- Sign major contracts
- Raise capital
- Hire key people

### Money Magnetism Strategy for Life Path {life_path}
- {name}'s unique wealth blueprint
- How money flows to Life Path {life_path}
- Best revenue models
- Investment strategy aligned with numbers
- Marketing approach that attracts abundance

---

## PART 6: CAREER & LIFE PURPOSE

### Your Divine Calling
4-5 paragraphs on {name}'s true purpose and soul mission

### Ideal Career Paths (Top 15)
Rank and detail 15 specific careers for Life Path {life_path}:
For each career include:
- Why perfect for {name}
- Skills they already have
- Skills to develop
- First 3 steps to pursue
- Income potential
- Fulfillment rating /10
- Best age to pursue

### Career Development Roadmap {current_year}-2030
Year-by-year professional guidance

### Side Hustle & Passive Income Ideas
10 specific ideas aligned with Life Path {life_path}

---

## PART 7: RELATIONSHIPS & LOVE

### Relationship Blueprint for Life Path {life_path}
5 paragraphs on what {name} needs in partnership

### Detailed Compatibility Analysis
For each Life Path (1-9, 11, 22, 33):
- Romantic compatibility percentage
- Sexual chemistry score /10
- Emotional connection /10
- Intellectual match /10
- Spiritual alignment /10
- Long-term potential /10
- What works and challenges
- How to make it work

### Love Forecast {current_year}-2050
- Best years to meet soulmate
- Best years for marriage
- Challenging relationship years
- Ages of major relationship shifts

### Twin Flame & Soulmate Timing
- Likely Life Path numbers of twin flame
- Probable meeting timeframe
- Signs they've met their person

---

## PART 8: HEALTH & WELLNESS BLUEPRINT

### Physical Body & Life Path {life_path}
- Body systems needing attention
- Preventive care priorities
- Best exercise modalities
- Ideal diet type
- Sleep patterns
- Supplements for their vibration

### Mental & Emotional Health
- Thought patterns
- Emotional regulation strategies
- Therapy modalities that work best
- Stress management techniques

### Energy Medicine & Healing
- Best healing modalities
- Sound frequencies for their number
- Breath work practices

### Health Timing & Prevention
- Ages to pay extra attention
- Years requiring health focus
- Best months for health initiatives

---

## PART 9: YEAR-BY-YEAR FORECAST ({current_year}-2050)

For key years through 2050, provide:
- Main theme and energy
- Career focus
- Relationship developments
- Financial outlook
- Health considerations
- Spiritual growth area
- Best and challenging months
- Major decisions to make
- Affirmation for the year

Focus on milestone years: {current_year}, {current_year + 1}, {current_year + 5}, {current_year + 9}, and every 5 years after.

---

## PART 10: MONTHLY GUIDANCE FOR {current_year}

For each month provide:
- Energy theme
- Best activities
- What to avoid
- Lucky days
- Affirmation
- Action items

---

## PART 11: SPIRITUAL DEVELOPMENT PATH

### Soul Mission & Dharma
- Why {name}'s soul incarnated now
- Their role in planetary awakening
- Service to humanity
- Legacy they're here to create

### Spiritual Gifts & Abilities
Detail spiritual gifts and when they activate

### Sacred Practices for {name}
- Morning/evening rituals
- Meditation techniques
- Journaling prompts
- Moon rituals
- Prayer/mantras

---

## PART 12: PRACTICAL 90-DAY ACTION PLAN

### Days 1-30: Foundation
Weekly action steps

### Days 31-60: Building Momentum
Weekly action steps

### Days 61-90: Integration & Launch
Weekly action steps

### Quick Wins This Week
10 immediate actions

---

## PART 13: GOAL SETTING ALIGNED WITH DESTINY

### 1-Year Vision
Specific goals for career, finances, relationships, health, spirituality

### 5-Year Vision
Detailed vision at age {age + 5}

### 10-Year Vision
Detailed vision at age {age + 10}

### Life Vision by 2050
Pictures at ages {age + 15}, {age + 20}, {age + 25}, {age + 30}

---

## PART 14: POWER TOOLS & RESOURCES

### Affirmations & Mantras
30 powerful affirmations for Life Path {life_path}

### Visualization Scripts
3 detailed visualization journeys

### Decision-Making Framework
How to make important decisions based on numbers

---

## PART 15: MYSTERIES & ADVANCED INSIGHTS

### Hidden Potential
5-7 abilities they haven't discovered yet

### Karmic Allies & Teachers
Who will appear and when

### Synchronicity Patterns
Signs the Universe sends {name}

### The Ultimate Test
Major initiation for Life Path {life_path}

---

## CONCLUSION: YOUR COSMIC INVITATION

Write 5-6 final paragraphs of encouragement and empowerment

---

**WRITING INSTRUCTIONS:**
- Use {name}'s name 50+ times
- Write in warm second person ("you")
- Be specific with dates, ages, years
- Give actionable strategies
- Include calculations and percentages
- Make it feel like a $5000 consultation
- Be encouraging AND realistic
- Use metaphors and examples
- Write at 10th grade level
- Target: 15,000-20,000 words
- Make every section deeply valuable"""
            }]
        )
        
        # Extract report content
        report_content = message.content[0].text
        
        # Store lead with purchase flag
        if email:
            lead_id = f"lead_{datetime.now().timestamp()}"
            leads_db[lead_id] = {
                'id': lead_id,
                'email': email,
                'name': name,
                'birthdate': birthdate,
                'life_path': life_path,
                'created_at': datetime.now().isoformat(),
                'purchased_full_report': True
            }
        
        return jsonify({
            'success': True,
            'data': {
                'name': name,
                'life_path': life_path,
                'report': report_content,
                'generated_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error generating report: {error_detail}")
        return jsonify({'error': str(e), 'detail': error_detail}), 500


@app.route('/api/reports/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF version of report"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.lib.colors import HexColor
        
        data = request.json
        report_content = data.get('report')
        customer_name = data.get('name')
        life_path = data.get('life_path')
        
        if not report_content:
            return jsonify({'error': 'No report content provided'}), 400
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            topMargin=0.75*inch, 
            bottomMargin=0.75*inch,
            leftMargin=1*inch, 
            rightMargin=1*inch
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=HexColor('#667eea'),
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=24,
            fontName='Helvetica-Bold',
            keepWithNext=True
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            keepWithNext=True
        )
        
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            spaceAfter=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        )
        
        # Build document
        story = []
        
        # Title page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("THE COMPLETE LIFE BLUEPRINT", title_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Your Comprehensive Numerology Report", heading2_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Prepared for {customer_name}", heading2_style))
        story.append(Paragraph(f"Life Path Number: {life_path}", heading2_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", body_style))
        story.append(PageBreak())
        
        # Process report content
        lines = report_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                story.append(Spacer(1, 0.08*inch))
                continue
            
            # Skip horizontal rules
            if line.startswith('---'):
                story.append(Spacer(1, 0.15*inch))
                continue
            
            # Main headings (# )
            if line.startswith('# '):
                text = line.replace('# ', '').strip()
                story.append(PageBreak())
                story.append(Paragraph(text, heading1_style))
            
            # Subheadings (## )
            elif line.startswith('## '):
                text = line.replace('## ', '').strip()
                story.append(Spacer(1, 0.15*inch))
                story.append(Paragraph(text, heading2_style))
            
            # Sub-subheadings (### )
            elif line.startswith('### '):
                text = line.replace('### ', '').strip()
                story.append(Paragraph(text, heading3_style))
            
            # Handle bold/emphasis (**text**)
            else:
                # Convert markdown bold to HTML bold
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                # Convert single asterisks to italic
                text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
                
                try:
                    story.append(Paragraph(text, body_style))
                except:
                    # If paragraph fails, try with cleaned text
                    cleaned_text = text.replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(cleaned_text, body_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Return as downloadable file
        pdf_buffer = BytesIO(pdf_data)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Numerology_Report_{customer_name.replace(" ", "_")}.pdf'
        )
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"PDF Error: {error_detail}")
        return jsonify({'error': str(e), 'detail': error_detail}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
