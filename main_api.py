from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os
from io import BytesIO
import re

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

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
        
        # Generate comprehensive AI report
        current_year = datetime.now().year
        birth_date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
        age = current_year - birth_date_obj.year
        birth_month = birth_date_obj.month
        birth_day = birth_date_obj.day
        
        # Optimized prompt for faster generation
        prompt = f"""You are a master numerologist creating a premium personalized report.

Create a comprehensive numerology analysis for:
Name: {name}
Life Path Number: {life_path}
Birth Date: {birth_month}/{birth_day}/{birth_date_obj.year}
Current Age: {age}
Current Year: {current_year}

# COMPLETE NUMEROLOGY REPORT FOR {name}

## PART 1: YOUR LIFE PATH {life_path}

Write 4-5 paragraphs covering:
- Deep meaning of Life Path {life_path} for {name}
- Natural strengths and gifts (list 8-10 specific ones)
- Life lessons and challenges
- Soul purpose and mission

## PART 2: CAREER & MONEY

Write 3-4 paragraphs including:
- Ideal career paths (list top 10 with brief explanations)
- Best business opportunities
- Money manifestation strategy for Life Path {life_path}
- Professional development for {current_year}-{current_year + 5}

## PART 3: RELATIONSHIPS & LOVE

Write 3-4 paragraphs covering:
- What {name} needs in relationships
- Compatibility scores with Life Paths 1-9, 11, 22, 33 (give percentage for each)
- Best years for love: {current_year}-{current_year + 10}
- Twin flame and soulmate guidance

## PART 4: YEAR-BY-YEAR FORECAST

Provide guidance for these years:
- {current_year}: Main theme, opportunities, challenges
- {current_year + 1}: Focus areas and timing
- {current_year + 2}: Key developments
- {current_year + 5}: Major milestone year
- Ages {age + 5}, {age + 10}, {age + 15}: What to expect

## PART 5: SPIRITUAL GUIDANCE

Write 3 paragraphs on:
- Past life influences on this lifetime
- Spiritual gifts and psychic abilities
- Chakra system alignment for Life Path {life_path}
- Sacred practices and rituals

## PART 6: LUCKY TIMING & DATES

Provide:
- Best months in {current_year} for: career, love, money, health
- Lucky days of the month for Life Path {life_path}
- Optimal years for major life events through 2050

## PART 7: BUSINESS GUIDANCE

Include:
- Should {name} be an entrepreneur? (score 1-10)
- 5 business name suggestions with numerology calculations
- Best business launch timing in {current_year}-{current_year + 1}

## PART 8: ACTION PLAN

Provide:
- 90-day action plan (specific weekly steps)
- 1-year goals aligned with destiny
- 5-year vision for age {age + 5}
- Life vision for 2050

## PART 9: POWER TOOLS

Include:
- 15 powerful affirmations for Life Path {life_path}
- Daily rituals and practices
- Crystals, colors, and frequencies

## CONCLUSION

3-4 paragraphs of encouragement and empowerment

---
INSTRUCTIONS:
- Use {name}'s name 30+ times
- Write in warm second person ("you")
- Be specific with dates, ages, percentages
- Give actionable advice
- Target length: 4000-5000 words
- Make it feel personal and valuable"""
        
        # Stream response to prevent timeout
        full_report = ""
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                full_report += text
        
        # Store lead
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
                'report': full_report,
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