import { useState, useMemo } from 'react';
import SearchBar from '../components/SearchBar';
import LicitacionCard from '../components/LicitacionCard';
import LicitacionDetailModal from '../components/LicitacionDetailModal';
import { fetchLicitacionDetalle } from '../services/api';

const normalizeText = (text = '') =>
  text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');

export default function Dashboard({ licitacionesIniciales = [] }) {
  const [query, setQuery] = useState('');
  const [selectedLicitacion, setSelectedLicitacion] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [detalle, setDetalle] = useState(null);

  const licitacionesFiltradas = useMemo(() => {
    if (!query.trim()) return licitacionesIniciales;

    const normalizedQuery = normalizeText(query);
    const terms = normalizedQuery.split(' ').filter(Boolean);

    return licitacionesIniciales.filter((item) => {
      const target = normalizeText(`${item.id} ${item.nombre} ${item.organismo || ''}`);
      return terms.every((term) => target.includes(term));
    });
  }, [query, licitacionesIniciales]);

  const handleSelectLicitacion = async (item) => {
    setSelectedLicitacion(item);
    setLoadingDetail(true);
    setDetalle(null);

    const apiData = await fetchLicitacionDetalle(item.id);
    setDetalle(apiData || item);
    setLoadingDetail(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6 font-sans">
      <header className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Panel de Control de Licitaciones
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Exploración en tiempo real y consulta directa a Mercado Público
          </p>
        </div>
        <div className="flex gap-4">
          <div className="bg-slate-800/80 border border-slate-700/50 rounded-xl px-4 py-2 text-center">
            <span className="block text-2xl font-semibold text-emerald-400">
              {licitacionesFiltradas.length}
            </span>
            <span className="text-xs text-slate-400">Resultados</span>
          </div>
          <div className="bg-slate-800/80 border border-slate-700/50 rounded-xl px-4 py-2 text-center">
            <span className="block text-2xl font-semibold text-blue-400">
              {licitacionesIniciales.length}
            </span>
            <span className="text-xs text-slate-400">Total Cargadas</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-6">
        <SearchBar query={query} setQuery={setQuery} />

        {licitacionesFiltradas.length === 0 ? (
          <div className="text-center py-16 bg-slate-800/30 rounded-2xl border border-dashed border-slate-700">
            <p className="text-slate-400 text-base">No se encontraron licitaciones coincidentes.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {licitacionesFiltradas.map((item) => (
              <LicitacionCard
                key={item.id}
                item={item}
                onSelect={handleSelectLicitacion}
              />
            ))}
          </div>
        )}
      </main>

      <LicitacionDetailModal
        selectedLicitacion={selectedLicitacion}
        detalle={detalle}
        loadingDetail={loadingDetail}
        onClose={() => setSelectedLicitacion(null)}
      />
    </div>
  );
}