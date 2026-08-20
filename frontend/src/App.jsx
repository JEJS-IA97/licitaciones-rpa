import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export default function App() {
  const [licitaciones, setLicitaciones] = useState([]);
  const [selected, setSelected] = useState(null);
  const [analisis, setAnalisis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchLicitaciones();
  }, []);

  const fetchLicitaciones = async () => {
    try {
      const res = await axios.get(`${API_URL}/licitaciones/`);
      setLicitaciones(res.data.items);
    } catch (err) {
      console.error('Error cargando licitaciones', err);
    }
  };

  const analizarLicitacion = async (id) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/documentos/analizar/${id}`);
      setAnalisis(res.data);
    } catch (err) {
      alert('Error ejecutando análisis por IA. Verifica la carpeta de anexos.');
    } finally {
      setLoading(false);
    }
  };

  const generarDocumentos = async (id) => {
    if (!analisis) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/documentos/generar/${id}`, analisis);
      alert(`Archivos generados exitosamente: ${res.data.archivos_generados.join(', ')}`);
    } catch (err) {
      alert('Error al generar los documentos finales.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans">
      <header className="mb-8 border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-blue-400">RPA Mercado Público — Panel de Control</h1>
        <p className="text-slate-400 text-sm">Coimsa & Induwork Procurement Automation</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Listado */}
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h2 className="text-lg font-semibold mb-4 text-slate-200">Licitaciones Encontradas</h2>
          <div className="space-y-3 max-h-[70vh] overflow-y-auto">
            {licitaciones.map((lic) => (
              <div
                key={lic.id}
                onClick={() => { setSelected(lic); setAnalisis(null); }}
                className={`p-3 rounded-md cursor-pointer transition border ${selected?.id === lic.id ? 'bg-blue-900/40 border-blue-500' : 'bg-slate-700/50 border-transparent hover:bg-slate-700'}`}
              >
                <div className="text-xs text-blue-400 font-mono">{lic.id}</div>
                <div className="font-medium text-sm text-slate-200 line-clamp-2">{lic.nombre}</div>
                <div className="text-xs text-slate-400 mt-2">{lic.organismo}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Detalle y Ejecución */}
        <div className="lg:col-span-2 bg-slate-800 rounded-lg p-6 border border-slate-700">
          {selected ? (
            <div>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className="text-xs font-mono bg-blue-900 text-blue-300 px-2 py-1 rounded">{selected.id}</span>
                  <h2 className="text-xl font-bold mt-2 text-slate-100">{selected.nombre}</h2>
                  <p className="text-sm text-slate-400">{selected.organismo}</p>
                </div>
              </div>

              {/* Botones de Acción */}
              <div className="flex gap-3 my-6">
                <button
                  onClick={() => analizarLicitacion(selected.id)}
                  disabled={loading}
                  className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white px-4 py-2 rounded-md font-medium text-sm transition"
                >
                  {loading ? 'Procesando...' : '1. Analizar Anexos con IA'}
                </button>
                <button
                  onClick={() => generarDocumentos(selected.id)}
                  disabled={!analisis || loading}
                  className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white px-4 py-2 rounded-md font-medium text-sm transition"
                >
                  2. Generar Documentos Base
                </button>
              </div>

              {/* Resultados de IA */}
              {analisis && (
                <div className="bg-slate-900 rounded-md p-4 border border-slate-700 mt-4">
                  <h3 className="text-sm font-semibold text-purple-400 mb-2">Requerimientos Detectados por la IA:</h3>
                  <pre className="text-xs text-slate-300 overflow-x-auto whitespace-pre-wrap font-mono">
                    {JSON.stringify(analisis, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500 text-sm">
              Selecciona una licitación del listado para comenzar.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}