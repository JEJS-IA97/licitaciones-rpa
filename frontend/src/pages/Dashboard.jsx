// pages/Dashboard.jsx

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import { buscarLicitaciones, guardarLicitacion, fetchLicitacionesGuardadas, fetchLicitacionesPotenciales } from '../api';

export default function Dashboard() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(false);
    const [tab, setTab] = useState('guardadas');
    const [mensaje, setMensaje] = useState('');
    const [guardando, setGuardando] = useState({});
    const nav = useNavigate();

    useEffect(() => {
        if (tab === 'guardadas') cargarGuardadas();
        else if (tab === 'potenciales') cargarPotenciales();
    }, [tab]);

    const cargarGuardadas = async () => {
        setLoading(true);
        try {
            const data = await fetchLicitacionesGuardadas();
            setItems(data.payload?.items || []);
            setMensaje(`${items.length} licitaciones guardadas`);
        } catch (err) {
            setMensaje('Error cargando guardadas');
        } finally {
            setLoading(false);
        }
    };

    const cargarPotenciales = async () => {
        setLoading(true);
        try {
            const data = await fetchLicitacionesPotenciales();
            setItems(data.payload?.items || []);
            setMensaje(`${items.length} licitaciones potenciales detectadas`);
        } catch (err) {
            setMensaje('Error cargando potenciales');
        } finally {
            setLoading(false);
        }
    };

    const buscar = async (q) => {
        setTab('buscar');
        setLoading(true);
        setMensaje(`Buscando "${q}"...`);
        try {
            const data = await buscarLicitaciones(q);
            setItems(data.payload?.items || []);
            setMensaje(`${data.payload?.total || 0} resultados para "${q}"`);
        } catch (err) {
            setMensaje('Error en la búsqueda');
        } finally {
            setLoading(false);
        }
    };

    const guardar = async (id) => {
        setGuardando(prev => ({ ...prev, [id]: true }));
        try {
            await guardarLicitacion(id);
            alert('✅ Licitación guardada');
            if (tab === 'buscar') {
                // Recargar guardadas para actualizar el estado
                await cargarGuardadas();
            }
        } catch (err) {
            alert('Error al guardar: ' + err.message);
        } finally {
            setGuardando(prev => ({ ...prev, [id]: false }));
        }
    };

    const esGuardada = (id) => {
        // En la tab 'guardadas', todas ya están guardadas
        if (tab === 'guardadas') return true;
        // En otras tabs, verificar si está en la lista de guardadas (pero no tenemos esa lista fácilmente)
        // Simplificamos: siempre mostrar botón "Guardar" si no está en la lista de guardadas
        // Podemos mejorar con un estado global
        return false;
    };

    return (
        <div className="app">
            <Header />
            <div className="card">
                <h3>Panel de Licitaciones</h3>
                <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                  <button 
                        className={tab === 'buscar' ? 'button' : 'button secondary'}
                        onClick={() => setTab('buscar')}
                    >
                        Buscar
                    </button>
                    <button 
                        className={tab === 'guardadas' ? 'button' : 'button secondary'}
                        onClick={() => setTab('guardadas')}
                    >
                        Guardadas
                    </button>
                    <button 
                        className={tab === 'potenciales' ? 'button' : 'button secondary'}
                        onClick={() => setTab('potenciales')}
                    >
                      Potenciales
                    </button>
            
                </div>
                <p className="small" style={{marginTop:4}}>{mensaje}</p>
            </div>

            <div style={{marginTop:12}}>
                {tab === 'buscar' && <SearchBar onSearch={buscar} loading={loading} />}
                
                {loading ? (
                    <div className="card small">⏳ Cargando...</div>
                ) : (
                    <table className="table card">
                        <thead>
                            <tr>
                                <th>Código</th>
                                <th>Nombre</th>
                                <th>Estado</th>
                                <th>Monto</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items.length === 0 ? (
                                <tr><td colSpan="5" className="small">No hay licitaciones para mostrar</td></tr>
                            ) : (
                                items.map(it => {
                                    const id = it.codigo || it.id;
                                    return (
                                        <tr key={id}>
                                            <td>{id}</td>
                                            <td>{it.nombre}</td>
                                            <td>{it.estado?.glosa || '-'}</td>
                                            <td>{it.presupuesto?.monto_disponible ? `$${it.presupuesto.monto_disponible.toLocaleString()}` : '-'}</td>
                                            <td>
                                                <button className="button secondary" onClick={() => nav(`/detalle/${encodeURIComponent(id)}`)}>
                                                    Ver
                                                </button>
                                                {tab !== 'guardadas' && (
                                                    <button 
                                                        className="button" 
                                                        style={{marginLeft:8}}
                                                        onClick={() => guardar(id)}
                                                        disabled={guardando[id]}
                                                    >
                                                        {guardando[id] ? 'Guardando...' : 'Guardar'}
                                                    </button>
                                                )}
                                                {tab === 'guardadas' && (
                                                    <button 
                                                        className="button secondary" 
                                                        style={{marginLeft:8, color:'red'}}
                                                        onClick={() => {
                                                            if (confirm(`¿Eliminar ${id} de guardadas?`)) {
                                                                // Llamar a DELETE /api/licitaciones/guardar/{id}
                                                                // Implementar en api.js
                                                            }
                                                        }}
                                                    >
                                                        Eliminar
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })
                            )}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}