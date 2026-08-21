
export default function LicitacionCard({ item, onSelect }) {
  return (
    <article
      onClick={() => onSelect(item)}
      className="bg-slate-800/70 hover:bg-slate-800 border border-slate-700/80 hover:border-blue-500/50 rounded-xl p-5 cursor-pointer transition-all duration-200 flex flex-col justify-between hover:shadow-lg hover:shadow-blue-500/5 group"
    >
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="font-mono text-xs font-medium text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2.5 py-1 rounded-md">
            {item.id}
          </span>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {item.estado || 'Activa'}
          </span>
        </div>
        <h3 className="font-medium text-slate-200 text-sm leading-snug line-clamp-2 group-hover:text-blue-300 transition-colors">
          {item.nombre}
        </h3>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-700/50 flex items-center justify-between text-xs text-slate-400">
        <span className="truncate max-w-[180px]">
          {item.organismo || 'Mercado Público'}
        </span>
        <span className="text-blue-400 font-medium group-hover:translate-x-0.5 transition-transform flex items-center gap-1">
          Ver detalle
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
          </svg>
        </span>
      </div>
    </article>
  );
}