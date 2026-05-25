'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function Onboarding() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [formData, setFormData] = useState({ name: '', birthDate: '', birthPlace: '' })

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) { router.push('/'); return }
      setUser(user)
      supabase.from('users').select('*').eq('id', user.id).single().then(({ data }) => {
        if (data?.name) setFormData(p => ({ ...p, name: data.name }))
        if (data?.birth_date) router.push('/chat')
      })
    })
  }, [])

  const calculateLifePath = (birthDate: string) => {
    const digits = birthDate.replace(/-/g, '')
    let sum = digits.split('').reduce((a, d) => a + parseInt(d), 0)
    while (sum > 9 && sum !== 11 && sum !== 22 && sum !== 33) {
      sum = sum.toString().split('').reduce((a, d) => a + parseInt(d), 0)
    }
    return sum
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return
    setLoading(true)
    try {
      const lifePath = calculateLifePath(formData.birthDate)
      const { error } = await supabase.from('users').update({
        name: formData.name,
        birth_date: formData.birthDate,
        birth_place: formData.birthPlace || null,
        life_path: lifePath,
        questions_left: 5,
      }).eq('id', user.id)
      if (error) throw error
      router.push('/chat')
    } catch (err: any) {
      alert('Something went wrong: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Outfit:wght@300;400;500;600&display=swap');
        * { box-sizing:border-box; margin:0; padding:0; }
        body { background:#05040A !important; }
        @keyframes spin { to { transform:translate(-50%,-50%) rotate(360deg); } }
        @keyframes spin-rev { to { transform:translate(-50%,-50%) rotate(-360deg); } }
        @keyframes fadeUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        .ring { position:absolute; border-radius:50%; border:1px solid rgba(201,168,76,.12); top:50%; left:50%; }
        .r1 { width:180px;height:180px; animation:spin 30s linear infinite; }
        .r2 { width:320px;height:320px; animation:spin-rev 50s linear infinite; border-style:dashed; opacity:.4; }
        .r3 { width:480px;height:480px; animation:spin 80s linear infinite; opacity:.2; }
        .an-input { background:#12101F; border:1px solid rgba(201,168,76,.2); color:#EDE8DC; font-family:'Outfit',sans-serif; font-size:.9rem; padding:14px 16px; outline:none; width:100%; transition:border-color .2s; }
        .an-input:focus { border-color:#C9A84C; background:#1A1730; }
        .an-input::placeholder { color:#8B8470; }
        .gold-btn { background:#C9A84C; color:#05040A; font-family:'Outfit',sans-serif; font-size:.82rem; font-weight:600; letter-spacing:.12em; text-transform:uppercase; padding:16px; border:none; cursor:pointer; width:100%; transition:all .25s; }
        .gold-btn:hover { background:#E8C76A; }
        .gold-btn:disabled { opacity:.6; cursor:not-allowed; }
      `}</style>

      <div style={{ minHeight:'100vh', background:'#05040A', color:'#EDE8DC', fontFamily:"'Outfit',sans-serif", display:'flex', alignItems:'center', justifyContent:'center', padding:'40px 24px', position:'relative', overflow:'hidden' }}>

        {/* Background rings */}
        <div style={{ position:'absolute', top:'50%', left:'30%', width:'500px', height:'500px' }}>
          <div className="ring r1" /><div className="ring r2" /><div className="ring r3" />
        </div>
        <div style={{ position:'absolute', inset:0, background:'radial-gradient(ellipse 60% 70% at 30% 50%,rgba(201,168,76,.07) 0%,transparent 70%)' }} />

        <div style={{ position:'relative', zIndex:2, width:'100%', maxWidth:'460px', animation:'fadeUp .8s ease forwards' }}>

          {/* Logo */}
          <div style={{ textAlign:'center', marginBottom:'40px' }}>
            <div style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'1.4rem', fontWeight:600, color:'#C9A84C', marginBottom:'28px' }}>✦ Arthnumro</div>
            <h1 style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:'2.4rem', fontWeight:300, lineHeight:1.2, marginBottom:'10px' }}>
              Set up your <em style={{ fontStyle:'italic', color:'#C9A84C' }}>chart</em>
            </h1>
            <p style={{ fontSize:'.85rem', color:'#8B8470' }}>We need your birth details to calculate your numerology numbers</p>
          </div>

          {/* Free callout */}
          <div style={{ background:'rgba(201,168,76,.06)', border:'1px solid rgba(201,168,76,.15)', padding:'14px 18px', display:'flex', alignItems:'center', gap:'14px', marginBottom:'28px' }}>
            <span style={{ fontSize:'1.3rem' }}>🎁</span>
            <p style={{ fontSize:'.82rem', color:'#8B8470', lineHeight:1.6 }}><strong style={{ color:'#C9A84C' }}>5 free questions</strong> are waiting for you — your chart is being built right now.</p>
          </div>

          <form onSubmit={handleSubmit} style={{ display:'flex', flexDirection:'column', gap:'18px' }}>
            <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
              <label style={{ fontSize:'.68rem', letterSpacing:'.12em', textTransform:'uppercase', color:'#8B8470' }}>Full Name</label>
              <input className="an-input" type="text" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. Priya Sharma" required />
            </div>

            <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
              <label style={{ fontSize:'.68rem', letterSpacing:'.12em', textTransform:'uppercase', color:'#8B8470' }}>Date of Birth</label>
              <input className="an-input" type="date" value={formData.birthDate} onChange={e => setFormData({ ...formData, birthDate: e.target.value })} required />
              <p style={{ fontSize:'.72rem', color:'#8B8470' }}>Used to calculate your Life Path, Personal Year, and chart numbers</p>
            </div>

            <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
              <label style={{ fontSize:'.68rem', letterSpacing:'.12em', textTransform:'uppercase', color:'#8B8470' }}>Birth Place <span style={{ opacity:.5 }}>(optional)</span></label>
              <input className="an-input" type="text" value={formData.birthPlace} onChange={e => setFormData({ ...formData, birthPlace: e.target.value })} placeholder="e.g. Mumbai, India" />
            </div>

            <button type="submit" className="gold-btn" disabled={loading} style={{ marginTop:'8px' }}>
              {loading ? 'Building your chart...' : 'Start My Reading ✦'}
            </button>
          </form>

          <p style={{ textAlign:'center', fontSize:'.75rem', color:'#8B8470', marginTop:'20px' }}>
            Your data is private and used only to personalise your readings
          </p>
        </div>
      </div>
    </>
  )
}
