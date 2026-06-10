// src/composables/useDarkMode.js
import { ref, onMounted } from 'vue';

const STORAGE_KEY = 'skay-dark-mode';

export function useDarkMode() {
  const isDark = ref(false);
  let themeChangeTimeout = null;
  let isApplying = false;
  
  const loadPreference = () => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved !== null) {
      isDark.value = saved === 'true';
    } else {
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    applyTheme();
  };
  
  const applyTheme = () => {
    if (isApplying) return;
    isApplying = true;
    
    if (isDark.value) {
      document.documentElement.classList.add('dark-theme');
      document.body.classList.add('dark-theme');
    } else {
      document.documentElement.classList.remove('dark-theme');
      document.body.classList.remove('dark-theme');
    }
    
    // Clear any pending timeout
    if (themeChangeTimeout) clearTimeout(themeChangeTimeout);
    
    // Dispatch event once after a short delay
    themeChangeTimeout = setTimeout(() => {
      window.dispatchEvent(new CustomEvent('theme-change', { detail: { isDark: isDark.value } }));
      setTimeout(() => {
        isApplying = false;
      }, 100);
    }, 100);
  };
  
  const toggleDarkMode = () => {
    isDark.value = !isDark.value;
    localStorage.setItem(STORAGE_KEY, isDark.value);
    applyTheme();
  };
  
  onMounted(() => {
    loadPreference();
  });
  
  return {
    isDark,
    toggleDarkMode
  };
}