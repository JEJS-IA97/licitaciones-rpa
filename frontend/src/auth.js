export function isAuthenticated() {
    return !!localStorage.getItem('token');
}

export function requireAuth(navigate) {
    if (!isAuthenticated()) navigate('/login');
}
