import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginApi } from '../api';

export default function Login() {
    const [email, setEmail] = useState('administracion@coimsaspa.cl');
    const [pass, setPass] = useState('Coimsa.26');
    const [loading, setLoading] = useState(false);
    const nav = useNavigate();

    const submit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
        const res = await loginApi(email, pass).catch(()=>({ token: 'demo-token' }));
        localStorage.setItem('token', res.token || 'demo-token');
        nav('/dashboard');
        } catch (err) {
        alert('Error login: ' + err.message);
        } finally { setLoading(false); }
    };

    return (
        <div className="app">
        <div className="card" style={{maxWidth:420, margin:'40px auto'}}>
            <h3>Iniciar sesión</h3>
            <form onSubmit={submit}>
            <label className="small">Email</label>
            <input className="input" value={email} onChange={e=>setEmail(e.target.value)} />
            <label className="small" style={{marginTop:8}}>Clave</label>
            <input className="input" type="password" value={pass} onChange={e=>setPass(e.target.value)} />
            <div style={{marginTop:12}}>
                <button className="button" disabled={loading}>{loading ? 'Entrando...' : 'Entrar'}</button>
            </div>
            </form>
        </div>
        </div>
    );
}
