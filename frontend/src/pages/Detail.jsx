// pages/Detail.jsx

import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../components/Header';
import { fetchLicitacionDetalle, triggerAnalizarAnexos, triggerAplicar, descargarAnexos } from '../api';

export default function Detail() {
    const { id } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [descargando, setDescargando] = useState(false);
    const [anexos, setAnexos] = useState([]);
    const [mensajeAnexos, setMensajeAnexos] = useState('');

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const res = await fetchLicitacionDetalle(id);
                setData(res.payload || null);
                // Verificar si ya hay anexos descargados
                const anexosRes = await fetch(`http://localhost:8000/api/licitaciones/${id}/descargar-anexos`, {
                    method: 'POST'
                });
                if (anexosRes.ok) {
                    const anexosData = await anexosRes.json();
                    if (anexosData.archivos) {
                        setAnexos(anexosData.archivos);
                        setMensajeAnexos(`✅ ${anexosData.archivos.length} anexos descargados`);
                    }
                }
            } catch (err) {
                alert('Error: ' + err.message);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [id]);

    const descargarAnexosHandler = async () => {
        setDescargando(true);
        setMensajeAnexos('⏳ Descargando anexos...');
        try {
            const res = await descargarAnexos(id);
            if (res.archivos) {
                setAnexos(res.archivos);
                setMensajeAnexos(`✅ ${res.archivos.length} anexos descargados correctamente`);
            } else {
                setMensajeAnexos('⚠️ No se encontraron anexos para descargar');
            }
        } catch (err) {
            setMensajeAnexos('❌ Error al descargar anexos: ' + err.message);
        } finally {
            setDescargando(false);
        }
    };

    const abrirCarpeta = () => {
        // En una aplicación de escritorio, esto abriría el explorador de archivos
        // En web, podrías mostrar los enlaces de descarga
        alert('Los anexos están guardados en la carpeta: storage/licitaciones_data/' + id + '/anexos_originales/');
    };

    if (loading) return <div className="app card">Cargando detalle...</div>;
    if (!data) return <div className="app card">No se encontró la licitación</div>;

    return (
        <div className="app">
            <Header />
            <div className="card">
                <h3>{data.nombre} <span className="small">({data.codigo})</span></h3>
                <p className="small">Estado: {data.estado?.glosa || data.estado?.codigo}</p>
                <p>{data.descripcion}</p>
            </div>

            <div style={{display:'grid', gridTemplateColumns:'1fr 360px', gap:12, marginTop:12}}>
                <div>
                    <div className="card">
                        <h4>Acciones</h4>
                        <button className="button" onClick={descargarAnexosHandler} disabled={descargando}>
                            {descargando ? 'Descargando...' : '📥 Descargar anexos'}
                        </button>
                        <button className="button" style={{marginLeft:8}} onClick={abrirCarpeta}>
                             Abrir carpeta
                        </button>
                        <button className="button" style={{marginLeft:8}} onClick={() => triggerAnalizarAnexos(id)}>
                             Analizar anexos
                        </button>
                        <button className="button" style={{marginLeft:8}} onClick={() => triggerAplicar(id, {})}>
                             Aplicar
                        </button>
                    </div>

                    {/* Sección de anexos descargados */}
                    <div className="card" style={{marginTop:12}}>
                        <h4>📎 Anexos descargados</h4>
                        <p className="small">{mensajeAnexos || 'No se han descargado anexos aún.'}</p>
                        {anexos.length > 0 ? (
                            <ul>
                                {anexos.map((archivo, idx) => (
                                    <li key={idx}>
                                        <a href={`/api/licitaciones/${id}/anexos/${encodeURIComponent(archivo)}`} target="_blank" rel="noreferrer">
                                            {archivo}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="small">No hay anexos descargados</p>
                        )}
                    </div>

                    <div className="card" style={{marginTop:12}}>
                        <h4>Productos solicitados</h4>
                        {data.productos_solicitados?.length ? (
                            <ul>
                                {data.productos_solicitados.map(p => <li key={p.codigo_producto}>{p.nombre} — {p.cantidad} {p.unidad_medida || ''}</li>)}
                            </ul>
                        ) : <p className="small">No hay productos listados</p>}
                    </div>
                </div>

                <div>
                    <div className="card">
                        <h4>Resumen</h4>
                        <p className="small">Monto estimado: {data.presupuesto?.monto_disponible || '-'}</p>
                        <p className="small">Organismo: {data.institucion?.organismo_comprador || '-'}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}