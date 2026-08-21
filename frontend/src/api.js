const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:3000/api';

async function request(path, opts = {}) {
    const token = localStorage.getItem('token');
    const headers = opts.headers || {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
    const res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
    if (!res.ok) {
        const text = await res.text();
        throw new Error(`${res.status} ${res.statusText} ${text}`);
    }
    return res.json();
}

export async function loginApi(email, password) {
  // En prototipo: backend puede validar o frontend simula
    return request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
}

export async function fetchLicitaciones(queryParams = '') {
    return request(`/licitaciones${queryParams ? `?${queryParams}` : ''}`);
}

export async function fetchLicitacionDetalle(id) {
    return request(`/licitaciones/${encodeURIComponent(id)}`);
}

export async function triggerAnalizarAnexos(id) {
    return request(`/licitaciones/${encodeURIComponent(id)}/analizar`, { method: 'POST' });
}

export async function triggerAplicar(id, payload) {
    return request(`/licitaciones/${encodeURIComponent(id)}/aplicar`, {
        method: 'POST',
        body: JSON.stringify(payload)
    });
}


export async function buscarLicitaciones(q, tamanoPagina = 25) {
    return request(`/licitaciones/buscar?q=${encodeURIComponent(q)}&tamano_pagina=${tamanoPagina}`);
}

export async function guardarLicitacion(id) {
    return request(`/licitaciones/guardar/${encodeURIComponent(id)}`, { method: 'POST' });
}

export async function fetchLicitacionesGuardadas() {
    return request(`/licitaciones/guardadas`);
}

export async function analizarConIA(id) {
    return request(`/licitaciones/${encodeURIComponent(id)}/analizar`, { method: 'POST' });
}

// Obtener licitaciones potenciales (las que la IA ha marcado como relevantes)
export async function fetchPotenciales() {
    return request('/licitaciones/potenciales');
}

// api.js

export async function fetchLicitacionesPotenciales() {
    return request('/licitaciones/potenciales');
}

export async function eliminarLicitacionGuardada(id) {
    return request(`/licitaciones/guardar/${encodeURIComponent(id)}`, { method: 'DELETE' });
}

export async function descargarAnexos(id) {
    return request(`/licitaciones/${encodeURIComponent(id)}/descargar-anexos`, { method: 'POST' });
}