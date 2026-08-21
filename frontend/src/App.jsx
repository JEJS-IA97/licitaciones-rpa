import Dashboard from './pages/Dashboard';

// Datos de prueba para inicializar el panel
const MOCK_LICITACIONES = [
  {
    id: "1057473-12-LR26",
    nombre: "Servicio de Guardias de Seguridad Privada",
    organismo: "Hospital Del Salvador",
    estado: "Activa"
  },
  {
    id: "1057480-48-LE26",
    nombre: "Adquisición de Detergentes multiusos y otros artículos de aseo",
    organismo: "Hospital San José de Melipilla",
    estado: "Activa"
  },
  {
    id: "1037-11-LR26",
    nombre: "ARRIENDO CAMIONES CARROZADOS PARA BRIGADAS DEPRIF",
    organismo: "CONAF",
    estado: "Activa"
  },
  {
    id: "1016414-20-LE26",
    nombre: "Bases Suscripciones del Servicio Adobe Creative",
    organismo: "Subsecretaría de Economía",
    estado: "Activa"
  }
];

export default function App() {
  return (
    <div className="min-h-screen bg-slate-900">
      <Dashboard licitacionesIniciales={MOCK_LICITACIONES} />
    </div>
  );
}