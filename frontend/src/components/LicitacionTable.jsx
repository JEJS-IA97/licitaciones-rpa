import { useNavigate } from 'react-router-dom';

export default function LicitacionTable({ items }) {
    const nav = useNavigate();
    return (
        <table className="table card">
        <thead>
            <tr>
            <th>Código</th>
            <th>Nombre</th>
            <th>Estado</th>
            <th>Fecha</th>
            <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
            {items.map(it => (
            <tr key={it.codigo}>
                <td>{it.codigo}</td>
                <td>{it.nombre}</td>
                <td>{it.estado?.glosa || it.estado?.codigo}</td>
                <td className="small">{it.fechas?.fecha_publicacion || '-'}</td>
                <td>
                <button className="button secondary" onClick={()=>nav(`/detalle/${encodeURIComponent(it.codigo)}`)}>Revisar</button>
                <button className="button" style={{marginLeft:8}} onClick={()=>nav(`/detalle/${encodeURIComponent(it.codigo)}?autoApply=1`)}>Aplicar</button>
                </td>
            </tr>
            ))}
        </tbody>
        </table>
    );
}
