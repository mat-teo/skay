import { createI18n } from 'vue-i18n';
import en from './locales/en.json';
import it from './locales/it.json';


function getInitialLanguage() {
  const savedLanguage = localStorage.getItem('user-language');
  if (savedLanguage) {
    return savedLanguage;
  }

  const browserLang = navigator.language || navigator.userLanguage;
  if (browserLang) {
    const shortLang = browserLang.split('-')[0]; 
    const supportedLanguages = ['en', 'it'];     
    
    if (supportedLanguages.includes(shortLang)) {
      return shortLang;
    }
  }

  
  return 'en';
}

const i18n = createI18n({
  legacy: false,          
  globalInjection: true,  
  locale: getInitialLanguage(),
  fallbackLocale: 'en',   
  messages: {
    en,
    it
    
  }
});

export default i18n;