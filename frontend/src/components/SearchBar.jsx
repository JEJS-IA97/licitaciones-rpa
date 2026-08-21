// SearchBar.jsx
import { useState } from 'react';

export default function SearchBar({ onSearch, loading }) {
    const [q, setQ] = useState('');
    const submit = (e) => {
        e.preventDefault();
        if (q.trim()) onSearch(q.trim());
    };
    return (
        <form className="search" onSubmit={submit}>
            <input 
                className="input" 
                placeholder="Buscar por código o palabra clave (ej: 2582-54-LP26, aseo, seguridad)" 
                value={q} 
                onChange={e => setQ(e.target.value)} 
                disabled={loading}
            />
            <button className="button" type="submit" disabled={loading}>
                {loading ? 'Buscando...' : 'Buscar en Mercado Público'}
            </button>
        </form>
    );
}