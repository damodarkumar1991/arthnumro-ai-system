'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

interface Message { id: string; role: 'user' | 'assistant'; content: string; created_at: string }

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://arthnumro-api.onrender.com'

const SUGGESTIONS = [
  'What does my Life Path number mean?',
  'Is this a good time to change careers?',
  'What are my lucky numbers this month?',
  'Analyse my compatibility with Life Path 4',
  'What does my Personal Year mean for me?',
]

export default function Chat() {
  const router = useRouter()
  const [userData, setUserData] = useState<any>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [questionsLeft, setQuestionsLeft] = useState(0)
  const [showTopup, setShowTopup] = useState(false)
  const [selectedPack, setSelectedPack] = useState('explorer')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => { loadUser() }, [])
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  const loadUser = async () => {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) { router.push('/'); return }
    const { data } = await supabase.from('users').select('*').eq('id', user.id).single()
    if (!data) { router.push('/'); return }
    if (!data.birth_date) { router.push('/onboarding'); return }
    setUserData(data)
    setQuestionsLeft(data.questions_left ?? data.token_balance ?? 0)
    // Load message history
    const { data: msgs } = await supabase.from('messages').select('*').eq('user_id', user.id).order('created_at', { ascending: true }).limit(50)
    if (msgs) setMessages(msgs)
  }

  const sendMessage = async (text?: string) => {
    const msg = (text || input).trim()
    if (!msg || !userData) return
    if (questionsLeft <= 0) { setShowTopup(true); return }

    setLoading(true)
    setInput('')

    const tempId = 'tmp-' + Date.now()
    const userMsg: Message = { id: tempId, role: 'user', content: msg, created_at: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])

    try {
      const res = await fetch(`${API_URL}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: msg,
          user_data: {
            name: userData.name,
            life_path: userData.life_path,
            birth_date: userData.birth_date,
            birth_place: userData.birth_place,
          }
        })
      })

      const data = await res.json()
      if (!data.success) throw new Error(data.error || 'No response')

      const aiMsg: Message = { id: 'ai-' + Date.now(), role: 'assistant', content: data.response, created_at: new Date().toISOString() }
      setMessages(prev => [...prev.filter(m => m.id !== tempId), { ...userMsg, id: 'u-' + Date.now() }, aiMsg])

      // Decrement questions and save to DB
      const newQ = Math.max(0, questionsLeft - 1)
      setQuestionsLeft(newQ)
      await supabase.from('users').update({ questions_left: newQ }).eq('id', userData.id)
      await supabase.from('messages').insert([
        { user_id: userData.id, role: 'user', content: msg, tokens_used: 0 },
        { user_id: userData.id, role: 'assistant', content: data.response, tokens_used: 1 }
      ])

      if (newQ <= 0) setShowTopup(true)

    } catch (err: any) {
      setMessages(prev => prev.filter(m => m.id !== tempId))
      alert('Error: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  const qPct = Math.min((questionsLeft / 20) * 100, 100)

  if (!userData) return (
    <div style={{ minHeight:'100vh', background:'#05040A', display:'flex', alignItems:'center', justifyContent:'center', color:'#C9A84C', fontFamily:"'Cormorant Garamond',serif", fontSize:'1.4rem', fontStyle:'italic' }}>
      Reading your chart...
    </div>
  )

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Outfit:wght@300;400;500;600&display=swap');
        * { box-sizing:border-box; margin:0; padding:0; }
        body { background:#05040A !important; overflow:hidden; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
        @keyframes bounce { 0%,80%,100% { transform:translateY(0); opacity:.4; } 40% { transform:translateY(-5px); opacity:1; } }
        .msg-in { animation:fadeUp .3s ease; }
        .suggestion { background:transparent; border:1px solid rgba(201,168,76,.15); color:#8B8470; font-family:'Outfit',sans-serif; font-size:.78rem; text-align:left; padding:10px 12px; cursor:pointer; transition:all .2s; line-height:1.4; width:100%; }
        .suggestion:hover { border-color:rgba(201,168,76,.35); color:#EDE8DC; background:rgba(201,168,76,.04); }
        .chat-input { flex:1; background:#12101F; border:1px solid rgba(201,168,76,.2); color:#EDE8DC; font-family:'Outfit',sans-serif; font-size:.9rem; font-weight:300; padding:12px 16px; resize:none; outline:none; min-height:48px; max-height:120px; transition:border-color .2s; }
        .chat-input:focus { border-color:#C9A84C; }
        .chat-input::placeholder { color:#8B8470; }
        .send-btn { background:#C9A84C; border:none; width:48px; height:48px; cursor:pointer; color:#05040A; font-size:1.1rem; flex-shrink:0; transition:all .2s; display:flex; align-items:center; justify-content:center; }
        .send-btn:hover { background:#E8C76A; }
        .send-btn:disabled { opacity:.5; cursor:not-allowed; }
        .pack-opt { background:#1A1730; border:1px solid rgba(201,168,76,.15); padding:16px 20px; cursor:pointer; transition:all .2s; display:flex; align-items:center; gap:16px; position:relative; }
        .pack-opt:hover, .pack-opt.sel { border-color:#C9A84C; }
        .pack-opt.sel::after { content:'✓'; position:absolute; top:12px; right:14px; color:#C9A84C; font-size:.8rem; }
        ::-webkit-scrollbar { width:4px; } ::-webkit-scrollbar-track { background:transparent; } ::-webkit-scrollbar-thumb { background:#1A1730; border-radius:2px; }
      `}</style>

      <div style={{ height:'100vh', display:'flex', background:'#05040A', color:'#EDE8DC', fontFamily:"'Outfit',sans-serif", overflow:'hidden' }}>

        {/* ── SIDEBAR ── */}
        <div style={{ width:'272px', background:'#0C0B16', borderRight:'1px solid rgba(201,168,76,.12)', display:'flex', flexDirection:'column', flexShrink:0 }}>
          {/* Logo + user card */}
          <div style={{ padding:'24px 20px', borderBottom:'1px solid rgba(201,168,76,.12)' }}>
            <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.2rem', fontWeight:600, color:'#C9A84C', marginBottom:'20px' }}>✦ Arthnumro</div>
            <div style={{ background:'#12101F', border:'1px solid rgba(201,168,76,.12)', padding:'14px 16px' }}>
              <div style={{ fontSize:'.92rem', fontWeight:500, marginBottom:'2px' }}>{userData.name}</div>
              <div style={{ fontSize:'.72rem', color:'#8B8470', marginBottom:'14px' }}>Life Path {userData.life_path}</div>
              {/* Question meter */}
              <div style={{ display:'flex', justifyContent:'space-between', fontSize:'.68rem', letterSpacing:'.08em', textTransform:'uppercase', color:'#8B8470', marginBottom:'6px' }}>
                <span>Questions</span>
                <span style={{ color:'#C9A84C', fontWeight:500 }}>{questionsLeft} left</span>
              </div>
              <div style={{ height:'3px', background:'#1A1730', borderRadius:'2px', overflow:'hidden' }}>
                <div style={{ height:'100%', width:`${qPct}%`, background:questionsLeft <= 2 ? '#D4857A' : 'linear-gradient(to right,#C9A84C,#E8C76A)', transition:'width .4s ease' }} />
              </div>
              <button onClick={() => setShowTopup(true)} style={{ display:'block', width:'100%', marginTop:'12px', background:'transparent', border:'1px solid rgba(201,168,76,.3)', color:'#C9A84C', fontFamily:"'Outfit',sans-serif", fontSize:'.7rem', letterSpacing:'.1em', textTransform:'uppercase', padding:'7px', cursor:'pointer', transition:'all .2s' }}>
                + Buy more questions
              </button>
            </div>
          </div>

          {/* Chart numbers */}
          <div style={{ padding:'18px 20px', borderBottom:'1px solid rgba(201,168,76,.12)' }}>
            <div style={{ fontSize:'.63rem', letterSpacing:'.15em', textTransform:'uppercase', color:'#8B8470', marginBottom:'12px' }}>Your Chart</div>
            {[['Life Path', userData.life_path], ['Personal Year', ((userData.life_path || 0) + new Date().getFullYear()) % 9 || 9]].map(([k, v]) => (
              <div key={String(k)} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'7px 0', borderBottom:'1px solid rgba(201,168,76,.06)', fontSize:'.82rem', color:'#8B8470' }}>
                <span>{k}</span>
                <span style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.1rem', color:'#C9A84C' }}>{v}</span>
              </div>
            ))}
          </div>

          {/* Suggestions */}
          <div style={{ padding:'18px 20px', flex:1, overflowY:'auto' }}>
            <div style={{ fontSize:'.63rem', letterSpacing:'.15em', textTransform:'uppercase', color:'#8B8470', marginBottom:'12px' }}>Ask about...</div>
            {SUGGESTIONS.map(s => (
              <button key={s} className="suggestion" style={{ marginBottom:'8px' }} onClick={() => { setInput(s); inputRef.current?.focus() }}>{s}</button>
            ))}
          </div>

          {/* Footer */}
          <div style={{ padding:'14px 20px', borderTop:'1px solid rgba(201,168,76,.12)', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
            <span style={{ fontSize:'.72rem', color:'#8B8470' }}>Arthnumro AI</span>
            <button onClick={handleSignOut} style={{ background:'transparent', border:'none', fontSize:'.7rem', letterSpacing:'.08em', textTransform:'uppercase', color:'#8B8470', cursor:'pointer', fontFamily:"'Outfit',sans-serif" }}>Sign out</button>
          </div>
        </div>

        {/* ── MAIN CHAT ── */}
        <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>
          {/* Topbar */}
          <div style={{ padding:'16px 24px', borderBottom:'1px solid rgba(201,168,76,.12)', display:'flex', alignItems:'center', gap:'12px', background:'#05040A', flexShrink:0 }}>
            <div style={{ width:'36px', height:'36px', borderRadius:'50%', background:'linear-gradient(135deg,#C9A84C,#D4857A)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'1rem' }}>✦</div>
            <div>
              <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.1rem', fontWeight:400 }}>Arthnumro AI</div>
              <div style={{ fontSize:'.72rem', color:'#5CBF82' }}>● Online · Ready to read your chart</div>
            </div>
            <div style={{ marginLeft:'auto', textAlign:'right' }}>
              <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1rem', color:'#C9A84C', fontWeight:400 }}>{questionsLeft} questions left</div>
              <div style={{ fontSize:'.72rem', color:'#8B8470' }}>Life Path {userData.life_path}</div>
            </div>
          </div>

          {/* Messages */}
          <div style={{ flex:1, overflowY:'auto', padding:'28px 24px', display:'flex', flexDirection:'column', gap:'20px' }}>
            {/* Welcome */}
            {messages.length === 0 && (
              <div className="msg-in" style={{ display:'flex', gap:'12px', alignItems:'flex-start' }}>
                <div style={{ width:'32px', height:'32px', borderRadius:'50%', background:'linear-gradient(135deg,#C9A84C,#D4857A)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'.9rem', flexShrink:0 }}>✦</div>
                <div>
                  <div style={{ background:'#12101F', border:'1px solid rgba(201,168,76,.12)', borderLeft:'2px solid #C9A84C', padding:'14px 18px', fontSize:'.88rem', lineHeight:1.75 }}>
                    Welcome, <strong style={{ color:'#C9A84C' }}>{userData.name}</strong>. 🌟<br /><br />
                    I've built your numerological chart. Your <strong style={{ color:'#C9A84C' }}>Life Path {userData.life_path}</strong> tells me a great deal about you already.<br /><br />
                    You have <strong style={{ color:'#C9A84C' }}>{questionsLeft} questions</strong> to explore your chart. What would you like to know?
                  </div>
                  <div style={{ fontSize:'.62rem', color:'#8B8470', marginTop:'4px', paddingLeft:'4px' }}>Just now</div>
                </div>
              </div>
            )}

            {messages.map(m => (
              <div key={m.id} className="msg-in" style={{ display:'flex', gap:'12px', alignItems:'flex-start', flexDirection: m.role === 'user' ? 'row-reverse' : 'row' }}>
                <div style={{ width:'32px', height:'32px', borderRadius:'50%', background: m.role === 'user' ? '#1A1730' : 'linear-gradient(135deg,#C9A84C,#D4857A)', border: m.role === 'user' ? '1px solid rgba(201,168,76,.2)' : 'none', display:'flex', alignItems:'center', justifyContent:'center', fontSize: m.role === 'user' ? '.8rem' : '.9rem', flexShrink:0, color: m.role === 'user' ? '#8B8470' : undefined }}>
                  {m.role === 'user' ? (userData.name?.[0] || 'U') : '✦'}
                </div>
                <div style={{ maxWidth:'70%' }}>
                  <div style={m.role === 'user' ? { background:'rgba(201,168,76,.08)', border:'1px solid rgba(201,168,76,.3)', padding:'12px 16px', fontSize:'.88rem', lineHeight:1.7, color:'#C9A84C' } : { background:'#12101F', border:'1px solid rgba(201,168,76,.12)', borderLeft:'2px solid #C9A84C', padding:'14px 18px', fontSize:'.88rem', lineHeight:1.75 }}>
                    <div style={{ whiteSpace:'pre-wrap' }}>{m.content}</div>
                  </div>
                  <div style={{ fontSize:'.62rem', color:'#8B8470', marginTop:'4px', paddingLeft:'4px', textAlign: m.role === 'user' ? 'right' : 'left' }}>
                    {new Date(m.created_at).toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' })}
                  </div>
                </div>
              </div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <div style={{ display:'flex', gap:'12px', alignItems:'flex-start' }}>
                <div style={{ width:'32px', height:'32px', borderRadius:'50%', background:'linear-gradient(135deg,#C9A84C,#D4857A)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'.9rem', flexShrink:0 }}>✦</div>
                <div style={{ background:'#12101F', border:'1px solid rgba(201,168,76,.12)', borderLeft:'2px solid #C9A84C', padding:'14px 18px', display:'flex', gap:'5px', alignItems:'center' }}>
                  {[0, 0.2, 0.4].map((d, i) => (
                    <div key={i} style={{ width:'6px', height:'6px', borderRadius:'50%', background:'#C9A84C', animation:`bounce 1.2s ease infinite`, animationDelay:`${d}s`, opacity:.4 }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input bar */}
          <div style={{ padding:'14px 24px', borderTop:'1px solid rgba(201,168,76,.12)', background:'#0C0B16', flexShrink:0 }}>
            {questionsLeft <= 2 && questionsLeft > 0 && (
              <div style={{ background:'rgba(212,133,122,.08)', border:'1px solid rgba(212,133,122,.25)', padding:'10px 14px', marginBottom:'10px', display:'flex', justifyContent:'space-between', alignItems:'center', fontSize:'.78rem', color:'#D4857A' }}>
                <span>⚠ Only {questionsLeft} question{questionsLeft === 1 ? '' : 's'} remaining</span>
                <button onClick={() => setShowTopup(true)} style={{ background:'transparent', border:'1px solid rgba(212,133,122,.4)', color:'#D4857A', fontFamily:"'Outfit',sans-serif", fontSize:'.68rem', letterSpacing:'.08em', textTransform:'uppercase', padding:'4px 12px', cursor:'pointer' }}>Top up</button>
              </div>
            )}
            <div style={{ display:'flex', gap:'10px', alignItems:'flex-end' }}>
              <textarea ref={inputRef} className="chat-input" rows={1} value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKey} placeholder="Ask your numerologist anything..." disabled={loading || questionsLeft <= 0} />
              <button className="send-btn" onClick={() => sendMessage()} disabled={loading || !input.trim() || questionsLeft <= 0}>→</button>
            </div>
            <div style={{ display:'flex', justifyContent:'space-between', marginTop:'6px', fontSize:'.68rem', color:'#8B8470' }}>
              <span>Enter to send · Shift+Enter for new line</span>
              <span>{questionsLeft} questions remaining</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── TOPUP MODAL ── */}
      {showTopup && (
        <div onClick={e => { if (e.target === e.currentTarget) setShowTopup(false) }} style={{ position:'fixed', inset:0, background:'rgba(5,4,10,.85)', zIndex:500, display:'flex', alignItems:'center', justifyContent:'center', backdropFilter:'blur(8px)', padding:'24px' }}>
          <div style={{ background:'#12101F', border:'1px solid rgba(201,168,76,.2)', padding:'40px', maxWidth:'460px', width:'100%', position:'relative', animation:'fadeUp .3s ease' }}>
            <button onClick={() => setShowTopup(false)} style={{ position:'absolute', top:'16px', right:'18px', background:'none', border:'none', color:'#8B8470', fontSize:'1.1rem', cursor:'pointer' }}>✕</button>
            <h3 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.8rem', fontWeight:300, marginBottom:'8px' }}>Buy more <em style={{ fontStyle:'italic', color:'#C9A84C' }}>questions</em></h3>
            <p style={{ fontSize:'.83rem', color:'#8B8470', lineHeight:1.7, marginBottom:'28px' }}>Questions never expire. Pay once, use whenever you need clarity.</p>
            <div style={{ display:'flex', flexDirection:'column', gap:'10px', marginBottom:'20px' }}>
              {[
                { key:'starter',  qs:'5',  label:'Starter',  sub:'₹40 per question', price:'₹199' },
                { key:'explorer', qs:'20', label:'Explorer', sub:'₹25 per question · Most popular', price:'₹499' },
                { key:'seeker',   qs:'50', label:'Seeker',   sub:'₹20 per question · Best value', price:'₹999' },
              ].map(p => (
                <div key={p.key} className={`pack-opt${selectedPack === p.key ? ' sel' : ''}`} onClick={() => setSelectedPack(p.key)}>
                  <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'2rem', fontWeight:300, color:'#C9A84C', minWidth:'44px', lineHeight:1 }}>{p.qs}</div>
                  <div style={{ flex:1 }}>
                    <div style={{ fontSize:'.9rem', fontWeight:500, marginBottom:'2px' }}>{p.label}</div>
                    <div style={{ fontSize:'.75rem', color:'#8B8470' }}>{p.sub}</div>
                  </div>
                  <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.3rem', fontWeight:400 }}>{p.price}</div>
                </div>
              ))}
            </div>
            <button style={{ width:'100%', background:'#C9A84C', color:'#05040A', fontFamily:"'Outfit',sans-serif", fontSize:'.82rem', fontWeight:600, letterSpacing:'.12em', textTransform:'uppercase', padding:'16px', border:'none', cursor:'pointer', transition:'background .2s' }} onClick={() => alert('Razorpay integration coming soon! Your selected pack: ' + selectedPack)}>
              Pay via Razorpay ✦
            </button>
          </div>
        </div>
      )}
    </>
  )
}
