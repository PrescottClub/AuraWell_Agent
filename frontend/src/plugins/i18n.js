import { createI18n } from 'vue-i18n';
import en from '../locales/en.json';
import zh from '../locales/zh.json';

const i18n = createI18n({
  legacy: false, // Must be set to false to use Composition API
  locale: 'zh', // set default locale
  fallbackLocale: 'en', // set fallback locale
  messages: {
    en,
    zh,
  },
});

export default i18n;
