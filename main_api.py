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

# In-memory storage
leads_db = {}

def calculate_life_path(birthdate):
    """Calculate Life Path number from birthdate"""
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
    """Generate premium AI-powered numerology report"""
    try:
        import anthropic
        
        data = request.json
        name = data.get('name')
        birthdate = data.get('birthdate')
        birthtime = data.get('birthtime', 'Not provided')
        birthplace = data.get('birthplace', 'Not provided')
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
        
        # Calculate age and dates
        current_year = datetime.now().year
        birth_date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
        age = current_year - birth_date_obj.year
        birth_month = birth_date_obj.month
        birth_day = birth_date_obj.day
        
        # Premium AI prompt with clear structure
        prompt = f"""You are a master numerologist creating a premium, professional report worth $47.

Create a comprehensive, well-structured numerology analysis for:
- Full Name: {name}
- Birth Date: {birth_month}/{birth_day}/{birth_date_obj.year}
- Birth Time: {birthtime}
- Birth Place: {birthplace}
- Life Path Number: {life_path}
- Current Age: {age} years old
- Current Year: {current_year}

# PREMIUM NUMEROLOGY REPORT

## EXECUTIVE SUMMARY

Write a powerful 3-paragraph summary that captures:
- The essence of {name}'s soul and life purpose
- The most important message they need to hear right now
- What makes their journey unique and special

---

## SECTION 1: YOUR LIFE PATH {life_path} - THE FOUNDATION

### What Life Path {life_path} Means for You

Write 4-5 paragraphs explaining:
- The deep spiritual meaning of this path
- Why your soul chose this number
- What makes you different from others
- Your ultimate life purpose

### Your Natural Gifts & Strengths

List and explain 10 specific strengths:
1. [Strength]: How it shows up in your life and how to use it
2. [Strength]: Practical applications and examples
[Continue through 10]

### Your Life Lessons & Challenges

Describe 5-6 key lessons:
- What the lesson is
- Why you're learning it
- How to recognize when you're in it
- Steps to move through it successfully

---

## SECTION 2: YOUR LIFE JOURNEY - PAST, PRESENT & FUTURE

### THE PAST: Ages 0-{age} (Your Journey So Far)

Write 3-4 paragraphs about:
- Major themes in childhood (ages 0-18)
- Young adult years (ages 18-30) - key developments
- Recent years - how the past shaped you
- Patterns you've been working through

**Note:** When mentioning "age 33" or any specific age, always explain what that means - e.g., "At age 33 (the year {birth_date_obj.year + 33}, which was {current_year - (birth_date_obj.year + 33)} years ago)" so it's crystal clear.

### THE PRESENT: Age {age} in {current_year}

Write 3-4 paragraphs covering:
- Where you are right now in your journey
- Current life theme and energy
- What you're being called to focus on THIS YEAR
- Opportunities available to you right now
- Challenges to navigate in {current_year}

### THE FUTURE: Your Next 30 Years

**Ages {age + 1} to {age + 5} ({current_year + 1}-{current_year + 5}):**
For each year, provide:
- Main theme
- Key opportunities
- What to focus on
- Important decisions to make

**Ages {age + 6} to {age + 15} ({current_year + 6}-{current_year + 15}):**
Overview of this decade with major milestones at ages {age + 7}, {age + 10}, {age + 13}

**Ages {age + 16} to {age + 30} ({current_year + 16}-{current_year + 30}):**
Long-term vision and major life events at ages {age + 20}, {age + 25}, {age + 30}

Always use format: "Age X (year YYYY)" so it's clear.

---

## SECTION 3: CAREER & FINANCIAL SUCCESS

### Your Professional Path

Write 3 paragraphs on:
- Your ideal career direction
- Natural talents you can monetize
- Work environments where you thrive

### Top 10 Career Recommendations

For each career:
1. **[Career Title]**
   - Why it's perfect for you
   - Skills you already have
   - Income potential: $X-$Y
   - First steps to pursue it

### Financial Prosperity Timeline

- **{current_year}-{current_year + 2}:** Financial focus and opportunities
- **{current_year + 3}-{current_year + 5}:** Building wealth phase
- **{current_year + 6}-{current_year + 10}:** Peak earning years
- **Best years for major investments:** [list specific years]

---

## SECTION 4: LOVE & RELATIONSHIPS

### Your Relationship Blueprint

Write 3 paragraphs on:
- What you truly need in a partner
- Your love language and style
- Patterns to be aware of

### Compatibility Guide

For EACH Life Path number (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33), provide:

**Life Path {life_path} + Life Path [X]**
- Romantic Compatibility: X/100
- What works well: [2-3 points]
- Main challenges: [2 points]
- How to make it thrive: [advice]

### Love Timeline

- **{current_year}:** What to expect in love this year
- **{current_year + 1}-{current_year + 3}:** Relationship forecast
- **Best years to meet someone special:** [list years]
- **Best years for marriage/commitment:** [list years]
- **Soul mate indicators:** What to look for

---

## SECTION 5: HEALTH & WELLBEING

### Physical Health Guidance

- Body systems to nurture
- Exercise types that work best for you
- Nutritional guidance
- Sleep and rest needs
- Preventive care priorities

### Emotional & Mental Wellness

- Emotional patterns to understand
- Stress management strategies
- Mental health practices
- Work-life balance tips

### Health Timeline

- **Ages to prioritize health:** [list specific ages with years]
- **{current_year}:** Health focus areas
- **Long-term wellness strategy**

---

## SECTION 6: SPIRITUAL DEVELOPMENT

### Your Spiritual Gifts

Describe 5-7 spiritual abilities you have or will develop

### Sacred Practices for You

- Daily rituals
- Meditation techniques
- Journaling prompts
- Moon rituals
- Altar setup

### Your Soul's Evolution

- Where you are spiritually right now
- Next level of awakening
- How to accelerate your growth

---

## SECTION 7: YOUR 90-DAY ACTION PLAN

### Month 1: Foundation
- Week 1: [specific actions]
- Week 2: [specific actions]
- Week 3: [specific actions]
- Week 4: [specific actions]

### Month 2: Momentum
[Same structure]

### Month 3: Transformation
[Same structure]

### Quick Wins You Can Achieve This Week
List 10 immediate actions

---

## SECTION 8: POWER TOOLS

### 20 Affirmations for Life Path {life_path}

1. "I am..." [specific affirmation]
2. "I trust..." [specific affirmation]
[Continue through 20]

### Lucky Numbers & Timing

- Your power numbers: [list]
- Best days of the month: [list]
- Lucky colors: [list]
- Beneficial crystals: [list]

---

## CLOSING MESSAGE

Write 3-4 final paragraphs:
- Acknowledging their unique journey
- Empowering them to step into their power
- Invitation to live their highest potential
- Words of encouragement and blessing

---

**CRITICAL WRITING INSTRUCTIONS:**

1. **Always use full context for ages:** "At age 33 (in the year {birth_date_obj.year + 33})" not just "at age 33"
2. **Use {name}'s name 40+ times** throughout to make it personal
3. **Write in warm, encouraging second person** ("you", "your")
4. **Be specific:** Include exact years, ages, percentages, numbers
5. **Explain everything clearly:** Assume reader knows nothing about numerology
6. **No jargon without explanation**
7. **Make it actionable:** Every section should have practical steps
8. **Target length: 5,000-6,000 words**
9. **Professional tone:** This is a premium $47 product
10. **No blank sections:** Every part must be filled with valuable content"""

        # Generate with streaming to prevent timeout
        full_report = ""
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
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
                'birthtime': birthtime,
                'birthplace': birthplace,
                'life_path': life_path,
                'created_at': datetime.now().isoformat(),
                'purchased_full_report': True
            }
        
    # Send email with report
        try:
            import resend
            resend.api_key = os.environ.get('RESEND_API_KEY')
            
            email_params = {
                "from": "Arthnumro Reports <reports@arthnumro.com>",
                "to": [email],
                "subject": f"✨ Your Premium Numerology Report is Ready, {name}!",
                "html": f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #ffffff; padding: 30px; border: 1px solid #e2e8f0; }}
        .button {{ display: inline-block; padding: 15px 30px; background: #16a085; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
        .footer {{ background: #f9fafb; padding: 20px; text-align: center; font-size: 0.9em; color: #718096; border-radius: 0 0 10px 10px; }}
        .details {{ background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">✨ Your Numerology Report is Ready!</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.1em;">Premium Life Blueprint Analysis</p>
        </div>
        
        <div class="content">
            <p>Dear {name},</p>
            
            <p>Thank you for your purchase! Your personalized numerology report has been successfully generated.</p>
            
            <div class="details">
                <strong>Your Report Details:</strong><br>
                📊 Life Path Number: {life_path}<br>
                📅 Birth Date: {birthdate}<br>
                ⏰ Birth Time: {birthtime}<br>
                📍 Birth Place: {birthplace}<br>
                📄 Report Length: 5,000+ words
            </div>
            
            <p><strong>To access your full report:</strong></p>
            
            <div style="text-align: center;">
                <a href="https://www.arthnumro.com/pages/generate-report" class="button">
                    📖 View Your Report Online
                </a>
            </div>
            
            <p style="margin-top: 30px;"><strong>What's included in your report:</strong></p>
            <ul>
                <li>Executive Summary of your life purpose</li>
                <li>Past, Present & Future timeline analysis</li>
                <li>Career & financial guidance</li>
                <li>Love & relationship compatibility</li>
                <li>Health & wellness recommendations</li>
                <li>Spiritual development path</li>
                <li>90-day action plan</li>
                <li>20 personalized affirmations</li>
            </ul>
            
            <p><strong>💡 Tip:</strong> Bookmark the report page for easy access anytime!</p>
            
            <p style="margin-top: 30px;">If you have any questions, reply to this email.</p>
            
            <p>To your highest potential,<br>
            <strong>The Arthnumro Team</strong></p>
        </div>
        
        <div class="footer">
            <p>© {datetime.now().year} Arthnumro - Premium Numerology Services<br>
            <a href="https://www.arthnumro.com" style="color: #667eea;">www.arthnumro.com</a></p>
        </div>
    </div>
</body>
</html>
"""
            }
            
            resend.Emails.send(email_params)
            print(f"✅ Email sent successfully to {email}")
            
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}")
        
        return jsonify({
            'success': True,
            'data': {
                'name': name,
                'life_path': life_path,
                'birthdate': birthdate,
                'birthtime': birthtime,
                'birthplace': birthplace,
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
    """Generate premium PDF with professional design"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from reportlab.lib.colors import HexColor, white
        
        data = request.json
        report_content = data.get('report')
        customer_name = data.get('name')
        life_path = data.get('life_path')
        birthdate = data.get('birthdate', 'Not provided')
        birthtime = data.get('birthtime', 'Not provided')
        birthplace = data.get('birthplace', 'Not provided')
        
        if not report_content:
            return jsonify({'error': 'No report content provided'}), 400
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.5*inch,
            bottomMargin=0.75*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Cover page title
        cover_title = ParagraphStyle(
            'CoverTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=HexColor('#667eea'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Cover subtitle
        cover_subtitle = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontSize=18,
            textColor=HexColor('#764ba2'),
            spaceAfter=40,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Section headings
        h1_style = ParagraphStyle(
            'CustomH1',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=HexColor('#667eea'),
            spaceAfter=15,
            spaceBefore=30,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=HexColor('#667eea'),
            borderPadding=10,
            backColor=HexColor('#f0f4ff')
        )
        
        h2_style = ParagraphStyle(
            'CustomH2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=HexColor('#e2e8f0'),
            borderPadding=5
        )
        
        h3_style = ParagraphStyle(
            'CustomH3',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=HexColor('#2c3e50'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=16,
            spaceAfter=10,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        )
        
        # Build document
        story = []
        
        # COVER PAGE
        story.append(Spacer(1, 2.5*inch))
        story.append(Paragraph("✨ YOUR PREMIUM NUMEROLOGY REPORT ✨", cover_title))
        story.append(Paragraph("Complete Life Blueprint & Guidance", cover_subtitle))
        story.append(Spacer(1, 0.5*inch))
        
        # Cover details table
        cover_data = [
            ['Prepared For:', customer_name],
            ['Life Path Number:', str(life_path)],
            ['Birth Date:', birthdate],
            ['Birth Time:', birthtime],
            ['Birth Place:', birthplace],
            ['Report Generated:', datetime.now().strftime('%B %d, %Y')]
        ]
        
        cover_table = Table(cover_data, colWidths=[2*inch, 4*inch])
        cover_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#667eea')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, -2), 1, HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(cover_table)
        story.append(Spacer(1, 1*inch))
        
        # Footer text
        footer = Paragraph(
            "This report is a personalized analysis created exclusively for you.<br/>© Arthnumro - Premium Numerology Services",
            ParagraphStyle('Footer', parent=body_style, fontSize=9, textColor=HexColor('#718096'), alignment=TA_CENTER)
        )
        story.append(footer)
        story.append(PageBreak())
        
        # PROCESS REPORT CONTENT
        lines = report_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                story.append(Spacer(1, 0.1*inch))
                continue
            
            if line.startswith('---'):
                story.append(Spacer(1, 0.2*inch))
                continue
            
            # Main headings
            if line.startswith('# '):
                text = line.replace('# ', '').strip()
                story.append(PageBreak())
                story.append(Paragraph(text, h1_style))
            
            # Subheadings
            elif line.startswith('## '):
                text = line.replace('## ', '').strip()
                story.append(Spacer(1, 0.15*inch))
                story.append(Paragraph(text, h2_style))
            
            # Sub-subheadings
            elif line.startswith('### '):
                text = line.replace('### ', '').strip()
                story.append(Paragraph(text, h3_style))
            
            # Body text
            else:
                # Convert markdown
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
                
                try:
                    story.append(Paragraph(text, body_style))
                except:
                    cleaned = text.replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(cleaned, body_style))
        
        # Build PDF
        doc.build(story)
        
        pdf_data = buffer.getvalue()
        buffer.close()
        
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
        print(f"PDF Error: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)