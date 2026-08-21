export default function AnexosList({ anexos = [] }) {
    if (!anexos.length) return <div className="card small">No hay anexos</div>;
    return (
        <div className="card">
        <h4>Anexos</h4>
        <ul>
            {anexos.map(a => (
            <li key={a.id || a.name}>
                <a href={a.url} target="_blank" rel="noreferrer">{a.name || a.filename}</a>
            </li>
            ))}
        </ul>
        </div>
    );
    }
