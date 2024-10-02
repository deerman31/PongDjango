import { navigate } from './router.js';

// DOMContentLoadedはhtmlが完全に読み込まれた時にイベントが起こる。なお、html以外のcssなどの読み込みは待たない
document.addEventListener('DOMContentLoaded', async () => {
    setTheme(getPreferredTheme());
    if (!location.hash) {
        location.hash = '#/';
    }
    await navigate(location.hash);
});

const getStoredTheme = () => localStorage.getItem('theme');
const setStoredTheme = (theme) => localStorage.setItem('theme', theme);
function getPreferredTheme() {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
        return storedTheme;
    }
    const preferredTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    return preferredTheme;
}
function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);
    setStoredTheme(theme);
}

function toggleTheme() {
    const theme = getStoredTheme();
    setTheme(theme === 'dark' ? 'light' : 'dark');
}
window.toggleTheme = toggleTheme;
