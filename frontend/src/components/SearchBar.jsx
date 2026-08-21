
export default function SearchBar({ query, setQuery }) {
  return (
    <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 shadow-lg backdrop-blur-sm">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar por ID (ej: 1057473-12-LR26), título o rubro..."
          className="w-full bg-slate-900 border border-slate-700 text-slate-100 rounded-xl pl-11 pr-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder:text-slate-500"
        />
        <svg
          className="absolute left-3.5 top-3.5 h-5 w-5 text-slate-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      </div>
    </div>
  );
}