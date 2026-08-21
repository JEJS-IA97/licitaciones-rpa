export const fetchLicitacionDetalle = async (codigoId) => {
  try {
    const res = await fetch(
      `https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?codigo=${codigoId}&ticket=TU_TICKET_AQUI`
    );
    const data = await res.json();
    return data?.Listado?.[0] || null;
  } catch (error) {
    console.error("Error al consultar el detalle de la licitación:", error);
    return null;
  }
};