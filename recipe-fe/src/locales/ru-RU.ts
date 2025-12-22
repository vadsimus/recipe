import component from './ru-RU/component';
import globalHeader from './ru-RU/globalHeader';
import menu from './ru-RU/menu';
import pages from './ru-RU/pages';
import pwa from './ru-RU/pwa';
import settingDrawer from './ru-RU/settingDrawer';
import settings from './ru-RU/settings';

export default {
  'navBar.lang': 'Язык',
  'layout.user.link.help': 'Помощь',
  'layout.user.link.privacy': 'Конфиденциальность',
  'layout.user.link.terms': 'Условия',
  'app.preview.down.block': 'Скачать эту страницу в локальный проект',
  'app.welcome.link.fetch-blocks': 'Получить все блоки',
  'app.welcome.link.block-list': 'Быстрое создание стандартных страниц на основе разработки `block`',
  ...pages,
  ...globalHeader,
  ...menu,
  ...settingDrawer,
  ...settings,
  ...pwa,
  ...component,
};

