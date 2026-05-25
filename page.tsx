'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function Home() {
  const router = useRouter()
  const [tab, setTab] = useState<'signin' | 'signup'>('signup')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) router.push('/chat')
    })
  }, [])

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (tab === 'signup') {
        const { data, error } = await supabase.auth.signUp({ email, password, options: { data: { name } } })
        if (error) throw error
        if (data.user) router.push('/onboarding')
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        if (data.user) router.push('/chat')
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Outfit:wght@300;400;500;600&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #05040A !important; }
        .an-page { min-height: 100vh; background: #05040A; color: #EDE8DC; font-family: 'Outfit', sans-serif; }
        @keyframes spin { to { transform: translate(-50%,-50%) rotate(360deg); } }
        @keyframes spin-rev { to { transform: translate(-50%,-50%) rotate(-360deg); } }
        @keyframes fadeUp { from { opacity:0; transform:translateY(24px); } to { opacity:1; transform:translateY(0); } }
        @keyframes float { 0%,100% { transform:translateY(0); } 50% { transform:translateY(-8px); } }
        .ring { position:absolute; border-radius:50%; border:1px solid rgba(201,168,76,0.15); top:50%; left:50%; }
        .r1 { width:200px;height:200px; animation:spin 30s linear infinite; }
        .r2 { width:360px;height:360px; animation:spin-rev 50s linear infinite; border-style:dashed; opacity:.5; }
        .r3 { width:540px;height:540px; animation:spin 80s linear infinite; opacity:.25; }
        .r4 { width:740px;height:740px; animation:spin-rev 110s linear infinite; opacity:.12; border-style:dashed; }
        .fade1{animation:fadeUp .8s ease forwards .2s;opacity:0;}
        .fade2{animation:fadeUp .8s ease forwards .4s;opacity:0;}
        .fade3{animation:fadeUp .8s ease forwards .6s;opacity:0;}
        .fade4{animation:fadeUp .8s ease forwards .8s;opacity:0;}
        .fade5{animation:fadeUp .8s ease forwards 1s;opacity:0;}
        .gold-btn { background:#C9A84C; color:#05040A; font-family:'Outfit',sans-serif; font-size:.82rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; padding:16px 40px; border:none; cursor:pointer; clip-path:polygon(8px 0%,100% 0%,calc(100% - 8px) 100%,0% 100%); transition:all .25s; display:inline-block; text-decoration:none; }
        .gold-btn:hover { background:#E8C76A; transform:translateY(-2px); box-shadow:0 12px 40px rgba(201,168,76,.4); }
        .gold-btn:disabled { opacity:.6; cursor:not-allowed; transform:none; }
        .an-input { background:#12101F; border:1px solid rgba(201,168,76,.2); color:#EDE8DC; font-family:'Outfit',sans-serif; font-size:.9rem; padding:14px 16px; outline:none; width:100%; transition:border-color .2s; }
        .an-input:focus { border-color:#C9A84C; background:#1A1730; }
        .an-input::placeholder { color:#8B8470; }
        .section-divider { width:60px; height:1px; background:linear-gradient(to right,transparent,#C9A84C,transparent); margin:16px auto 0; }
        .feature-card { background:#12101F; border:1px solid rgba(201,168,76,.12); padding:36px 28px; transition:all .3s; }
        .feature-card:hover { background:#1A1730; transform:translateY(-4px); border-color:rgba(201,168,76,.3); }
        .pack-card { background:#12101F; border:1px solid rgba(201,168,76,.15); padding:24px; display:flex; align-items:center; gap:20px; transition:all .2s; }
        .pack-card.featured { border-color:#C9A84C; background:#1A1730; }
        .pack-card:hover { border-color:rgba(201,168,76,.4); }
        .auth-tab { background:transparent; border:none; font-family:'Outfit',sans-serif; font-size:.82rem; font-weight:400; letter-spacing:.1em; text-transform:uppercase; color:#8B8470; padding:12px 24px 14px; cursor:pointer; position:relative; transition:color .2s; }
        .auth-tab.active { color:#C9A84C; }
        .auth-tab.active::after { content:''; position:absolute; bottom:-1px; left:0; right:0; height:2px; background:#C9A84C; }
        .error-box { background:rgba(212,133,122,.1); border:1px solid rgba(212,133,122,.3); color:#D4857A; font-size:.82rem; padding:12px 16px; }
      `}</style>

      <div className="an-page">

        {/* ── NAV ── */}
        <nav style={{ position:'fixed', top:0, left:0, right:0, zIndex:100, display:'flex', alignItems:'center', justifyContent:'space-between', padding:'20px 48px', background:'linear-gradient(to bottom,rgba(5,4,10,.95),transparent)', backdropFilter:'blur(8px)' }}>
          <span style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.4rem', fontWeight:600, color:'#C9A84C', letterSpacing:'.05em' }}>✦ Arthnumro</span>
          <div style={{ display:'flex', gap:'32px', alignItems:'center' }}>
            {['How it Works','Pricing'].map(l => (
              <a key={l} href={`#${l.toLowerCase().replace(/ /g,'')}`} style={{ fontSize:'.78rem', letterSpacing:'.1em', textTransform:'uppercase', color:'#8B8470', textDecoration:'none' }}>{l}</a>
            ))}
            <a href="#auth" className="gold-btn" style={{ padding:'8px 24px', fontSize:'.75rem' }}>Sign In</a>
          </div>
        </nav>

        {/* ── HERO ── */}
        <section style={{ minHeight:'100vh', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', textAlign:'center', padding:'120px 24px 80px', position:'relative', overflow:'hidden' }}>
          <div style={{ position:'absolute', inset:0, background:'radial-gradient(ellipse 60% 50% at 50% 0%,rgba(201,168,76,.1) 0%,transparent 70%),radial-gradient(ellipse 40% 50% at 20% 50%,rgba(212,133,122,.06) 0%,transparent 60%)' }} />
          <div className="ring r1" /><div className="ring r2" /><div className="ring r3" /><div className="ring r4" />
          {/* Stars */}
          <div style={{ position:'absolute', inset:0, backgroundImage:'radial-gradient(1.5px 1.5px at 15% 25%,rgba(201,168,76,.8) 0%,transparent 100%),radial-gradient(1px 1px at 35% 65%,rgba(255,255,255,.5) 0%,transparent 100%),radial-gradient(1.5px 1.5px at 60% 15%,rgba(201,168,76,.6) 0%,transparent 100%),radial-gradient(1px 1px at 80% 45%,rgba(255,255,255,.4) 0%,transparent 100%),radial-gradient(1px 1px at 90% 75%,rgba(255,255,255,.3) 0%,transparent 100%)' }} />

          <p className="fade1" style={{ fontFamily:"'Outfit',sans-serif", fontSize:'.72rem', fontWeight:500, letterSpacing:'.22em', textTransform:'uppercase', color:'#C9A84C', marginBottom:'24px', position:'relative', zIndex:2 }}>◆ &nbsp; Ancient Wisdom · AI Precision &nbsp; ◆</p>

          <h1 className="fade2" style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'clamp(3rem,7vw,5.5rem)', fontWeight:300, lineHeight:1.1, marginBottom:'16px', position:'relative', zIndex:2 }}>
            Your numbers<br />hold the <em style={{ fontStyle:'italic', color:'#C9A84C' }}>answers</em>
          </h1>

          <p className="fade3" style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'clamp(1.2rem,2.5vw,1.8rem)', fontWeight:300, fontStyle:'italic', color:'#8B8470', marginBottom:'28px', position:'relative', zIndex:2 }}>An AI numerologist that knows you</p>

          <p className="fade4" style={{ fontSize:'.95rem', color:'#8B8470', maxWidth:'500px', lineHeight:1.8, marginBottom:'44px', position:'relative', zIndex:2 }}>
            Born on a specific date — your numerology chart is uniquely yours. Ask anything about your life path, relationships, or destiny.
          </p>

          <div className="fade5" style={{ display:'flex', gap:'16px', justifyContent:'center', flexWrap:'wrap', position:'relative', zIndex:2 }}>
            <a href="#auth" className="gold-btn">Begin Your Reading — Free</a>
            <a href="#howitworks" style={{ background:'transparent', color:'#EDE8DC', fontFamily:"'Outfit',sans-serif", fontSize:'.82rem', letterSpacing:'.1em', textTransform:'uppercase', padding:'15px 32px', border:'1px solid rgba(237,232,220,.2)', textDecoration:'none', transition:'all .25s', display:'inline-block' }}>See How It Works</a>
          </div>
        </section>

        {/* ── TRUST BAR ── */}
        <div style={{ background:'#12101F', borderTop:'1px solid rgba(201,168,76,.15)', borderBottom:'1px solid rgba(201,168,76,.15)', padding:'28px 48px', display:'flex', justifyContent:'center', gap:'80px', flexWrap:'wrap' }}>
          {[['5 Free','Questions on Signup'],['50,000+','Readings Delivered'],['4.9 ★','Average Rating'],['Vedic + Pythagorean','Dual Tradition']].map(([num, label]) => (
            <div key={label} style={{ textAlign:'center' }}>
              <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.6rem', fontWeight:600, color:'#C9A84C', lineHeight:1 }}>{num}</div>
              <div style={{ fontSize:'.7rem', letterSpacing:'.1em', textTransform:'uppercase', color:'#8B8470', marginTop:'4px' }}>{label}</div>
            </div>
          ))}
        </div>

        {/* ── HOW IT WORKS ── */}
        <section id="howitworks" style={{ maxWidth:'1100px', margin:'0 auto', padding:'100px 48px' }}>
          <p style={{ fontSize:'.7rem', fontWeight:500, letterSpacing:'.25em', textTransform:'uppercase', color:'#C9A84C', marginBottom:'14px', display:'flex', alignItems:'center', gap:'12px' }}>
            <span style={{ display:'inline-block', width:'30px', height:'1px', background:'#C9A84C' }} />The Process
          </p>
          <h2 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'clamp(2rem,4vw,3rem)', fontWeight:300, lineHeight:1.2, marginBottom:'56px' }}>
            Three steps to <em style={{ fontStyle:'italic', color:'#C9A84C' }}>clarity</em>
          </h2>
          <div style={{ display:'flex', flexDirection:'column', gap:0 }}>
            {[
              ['01', 'Share your birth details', 'Your name and date of birth are the foundation. Arthnumro builds your unique numerological chart instantly.'],
              ['02', 'Ask anything', 'Career timing, compatibility, personal year energy, lucky numbers — ask in plain language, receive deep answers.'],
              ['03', 'Receive your insight', 'Personalised, contextual readings that blend classical numerology with your specific life situation.'],
            ].map(([num, title, desc]) => (
              <div key={num} style={{ display:'flex', gap:'24px', padding:'32px 0', borderBottom:'1px solid rgba(201,168,76,.12)' }}>
                <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'3.5rem', fontWeight:300, color:'rgba(201,168,76,.2)', lineHeight:1, minWidth:'60px' }}>{num}</div>
                <div>
                  <h3 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.4rem', fontWeight:400, marginBottom:'8px' }}>{title}</h3>
                  <p style={{ fontSize:'.88rem', color:'#8B8470', lineHeight:1.7 }}>{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── FEATURES ── */}
        <div style={{ background:'#0C0B16', borderTop:'1px solid rgba(201,168,76,.12)', borderBottom:'1px solid rgba(201,168,76,.12)', padding:'80px 48px' }}>
          <div style={{ maxWidth:'1100px', margin:'0 auto' }}>
            <div style={{ textAlign:'center', marginBottom:'56px' }}>
              <p style={{ fontSize:'.7rem', letterSpacing:'.25em', textTransform:'uppercase', color:'#C9A84C', marginBottom:'14px' }}>What You Can Explore</p>
              <h2 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'clamp(2rem,4vw,3rem)', fontWeight:300 }}>Every dimension of your <em style={{ fontStyle:'italic', color:'#C9A84C' }}>chart</em></h2>
              <div className="section-divider" />
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))', gap:'2px' }}>
              {[['☽','Life Path & Destiny','Your core number, soul urge, and the grand arc of your life mission.'],['♃','Relationships & Compatibility','Analyse partner numbers and understand your most harmonious connections.'],['◈','Career & Timing','Personal year cycles reveal the optimal windows for launches and transitions.'],['✦','Spiritual & Shadow Work','Karmic debt numbers and hidden patterns shaping your subconscious journey.']].map(([icon, title, desc]) => (
                <div key={title} className="feature-card">
                  <div style={{ fontSize:'2rem', marginBottom:'20px', display:'block', animation:'float 4s ease infinite' }}>{icon}</div>
                  <h3 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.25rem', fontWeight:400, marginBottom:'10px' }}>{title}</h3>
                  <p style={{ fontSize:'.83rem', color:'#8B8470', lineHeight:1.7 }}>{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── PRICING ── */}
        <section id="pricing" style={{ maxWidth:'1100px', margin:'0 auto', padding:'100px 48px' }}>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'80px', alignItems:'center' }}>
            <div>
              <p style={{ fontSize:'.7rem', fontWeight:500, letterSpacing:'.25em', textTransform:'uppercase', color:'#C9A84C', marginBottom:'14px', display:'flex', alignItems:'center', gap:'12px' }}>
                <span style={{ display:'inline-block', width:'30px', height:'1px', background:'#C9A84C' }} />Simple Pricing
              </p>
              <h2 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'clamp(2rem,4vw,3rem)', fontWeight:300, lineHeight:1.2, marginBottom:'16px' }}>Pay per question,<br /><em style={{ fontStyle:'italic', color:'#C9A84C' }}>nothing more</em></h2>
              <p style={{ fontSize:'.9rem', color:'#8B8470', lineHeight:1.8, marginBottom:'28px' }}>No subscriptions. No monthly charges. Questions never expire — buy once, use anytime.</p>
              <div style={{ background:'rgba(201,168,76,.06)', border:'1px solid rgba(201,168,76,.15)', padding:'16px 20px', display:'flex', alignItems:'center', gap:'14px' }}>
                <span style={{ background:'#C9A84C', color:'#05040A', fontSize:'.65rem', fontWeight:600, letterSpacing:'.1em', textTransform:'uppercase', padding:'4px 12px', whiteSpace:'nowrap' }}>FREE</span>
                <p style={{ fontSize:'.83rem', color:'#8B8470' }}>Start with <strong style={{ color:'#EDE8DC' }}>5 free questions</strong> — no card required.</p>
              </div>
            </div>
            <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
              {[
                { label:'Starter', qs:'5', pq:'₹40 per question', price:'₹199', featured:false },
                { label:'Explorer', qs:'20', pq:'₹25 per question · Most popular', price:'₹499', featured:true },
                { label:'Seeker', qs:'50', pq:'₹20 per question · Best value', price:'₹999', featured:false },
              ].map(p => (
                <div key={p.label} className={`pack-card${p.featured ? ' featured' : ''}`} style={{ position:'relative' }}>
                  {p.featured && <span style={{ position:'absolute', top:'12px', right:'16px', fontSize:'.6rem', letterSpacing:'.1em', textTransform:'uppercase', color:'#C9A84C', background:'rgba(201,168,76,.1)', border:'1px solid rgba(201,168,76,.3)', padding:'3px 10px' }}>Most Popular</span>}
                  <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'2.5rem', fontWeight:300, color:'#C9A84C', minWidth:'50px', lineHeight:1 }}>{p.qs}</div>
                  <div style={{ flex:1 }}>
                    <div style={{ fontSize:'.95rem', fontWeight:500, marginBottom:'2px' }}>{p.label}</div>
                    <div style={{ fontSize:'.75rem', color:'#8B8470' }}>{p.pq}</div>
                  </div>
                  <div style={{ textAlign:'right' }}>
                    <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.4rem', fontWeight:400 }}>{p.price}</div>
                    <div style={{ fontSize:'.72rem', color:'#8B8470' }}>one-time</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── AUTH SECTION ── */}
        <div id="auth" style={{ background:'#0C0B16', borderTop:'1px solid rgba(201,168,76,.12)', padding:'80px 24px' }}>
          <div style={{ maxWidth:'460px', margin:'0 auto' }}>
            <div style={{ textAlign:'center', marginBottom:'40px' }}>
              <h2 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'2.5rem', fontWeight:300, marginBottom:'8px' }}>
                {tab === 'signup' ? <>Your chart is <em style={{ fontStyle:'italic', color:'#C9A84C' }}>waiting</em></> : <>Welcome <em style={{ fontStyle:'italic', color:'#C9A84C' }}>back</em></>}
              </h2>
              <p style={{ fontSize:'.85rem', color:'#8B8470' }}>{tab === 'signup' ? '5 free questions — no card required' : 'Sign in to continue your journey'}</p>
            </div>

            {/* Tabs */}
            <div style={{ display:'flex', borderBottom:'1px solid rgba(201,168,76,.15)', marginBottom:'36px' }}>
              <button className={`auth-tab${tab === 'signup' ? ' active' : ''}`} onClick={() => { setTab('signup'); setError('') }}>Create Account</button>
              <button className={`auth-tab${tab === 'signin' ? ' active' : ''}`} onClick={() => { setTab('signin'); setError('') }}>Sign In</button>
            </div>

            {tab === 'signup' && (
              <div style={{ background:'rgba(201,168,76,.06)', border:'1px solid rgba(201,168,76,.15)', padding:'14px 16px', fontSize:'.82rem', color:'#8B8470', marginBottom:'24px', lineHeight:1.6 }}>
                🎁 &nbsp;<strong style={{ color:'#C9A84C' }}>5 free questions</strong> — no credit card required. Start exploring your chart right now.
              </div>
            )}

            {error && <div className="error-box" style={{ marginBottom:'20px' }}>{error}</div>}

            <form onSubmit={handleAuth} style={{ display:'flex', flexDirection:'column', gap:'18px' }}>
              {tab === 'signup' && (
                <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
                  <label style={{ fontSize:'.68rem', letterSpacing:'.12em', textTransform:'uppercase', color:'#8B8470' }}>Your Name</label>
                  <input className="an-input" type="text" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Priya Sharma" required />
                </div>
              )}
              <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
                <label style={{ fontSize:'.68rem', letterSpacing:'.12em', textTransform:'uppercase', color:'#8B8470' }}>Email Address</label>
                <input className="an-input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@email.com" required />
              </div>
              <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
                <label style={{ fontSize:'.68rem', letterSpacing:'.12em', textTransform:'uppercase', color:'#8B8470' }}>Password</label>
                <input className="an-input" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Min. 6 characters" minLength={6} required />
              </div>
              <button type="submit" className="gold-btn" disabled={loading} style={{ marginTop:'8px', width:'100%', textAlign:'center' }}>
                {loading ? 'Please wait...' : tab === 'signup' ? 'Begin My Journey ✦' : 'Sign In ✦'}
              </button>
            </form>
          </div>
        </div>

        {/* ── FOOTER ── */}
        <footer style={{ background:'#05040A', borderTop:'1px solid rgba(201,168,76,.12)', padding:'32px 48px', display:'flex', justifyContent:'space-between', alignItems:'center', flexWrap:'wrap', gap:'16px' }}>
          <span style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.1rem', fontWeight:600, color:'#C9A84C' }}>Arthnumro</span>
          <span style={{ fontSize:'.75rem', color:'#8B8470' }}>© 2025 Arthnumro · DKTW · Lakshmi Engineering Solutions</span>
        </footer>

      </div>
    </>
  )
}
