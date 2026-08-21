
export default function LicitacionDetailModal({ selectedLicitacion, detalle, loadingDetail, onClose }) {
  if (!selectedLicitacion) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="bg-slate-900 border-l border-slate-800 w-full max-w-2xl h-full flex flex-col shadow-2xl p-6 overflow-y-auto">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <span className="font-mono text-xs text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-1 rounded">
              {selectedLicitacion.id}
            </span>
            <h2 className="text-xl font-bold text-white mt-2">Detalle de Licitación</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="mt-6 flex-1 space-y-6">
          {loadingDetail ? (
            <div className="flex flex-col items-center justify-center h-64 space-y-3">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-slate-400 text-sm">Consultando API Mercado Público...</p>
            </div>
          ) : (
            <>
              <section className="bg-slate-800/50 p-4 rounded-xl border border-slate-800 space-y-2">
                <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Nombre / Título</p>
                <p className="text-slate-200 text-sm font-medium">{detalle?.Nombre || detalle?.nombre}</p>
              </section>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Organismo</p>
                  <p className="text-slate-200 text-sm mt-1">{detalle?.Comprador?.NombreOrganismo || detalle?.organismo || 'N/A'}</p>
                </div>
                <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Estado</p>
                  <p className="text-emerald-400 font-medium text-sm mt-1">{detalle?.Estado || detalle?.estado || 'Activa'}</p>
                </div>
              </div>

              <section className="bg-slate-800/50 p-4 rounded-xl border border-slate-800 space-y-2">
                <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Descripción</p>
                <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
                  {detalle?.Descripcion || 'Sin descripción adicional en la ficha.'}
                </p>
              </section>

              {detalle?.Fechas && (
                <section className="bg-slate-800/50 p-4 rounded-xl border border-slate-800 space-y-2">
                  <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Fechas del Proceso</p>
                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                    <div><span className="text-slate-500">Cierre:</span> {detalle.Fechas.FechaCierre || 'N/A'}</div>
                    <div><span className="text-slate-500">Publicación:</span> {detalle.Fechas.FechaCreacion || 'N/A'}</div>
                  </div>
                </section>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}