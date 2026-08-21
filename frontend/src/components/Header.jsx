import { useNavigate } from 'react-router-dom';

export default function Header() {
    const nav = useNavigate();
    const logout = () => {
        localStorage.removeItem('token');
        nav('/login');
    };
    return (
        <div className="header">
        <div style={{display:'flex',alignItems:'center',gap:12}}>
            <img src="/src/assets/logo.png" alt="logo" style={{height:150}}/>
            <h2>Licitaciones</h2>
        </div>
        <div>
            <button className="button secondary" onClick={()=>nav('/dashboard')}>Dashboard</button>
            <button className="button" style={{marginLeft:8}} onClick={logout}>Cerrar sesión</button>
        </div>
        </div>
    );
}
