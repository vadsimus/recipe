import type { ProLayoutProps } from '@ant-design/pro-components';

/** Brand palette for "Your Recipe" — warm, food-forward, and calm. */
export const brand = {
  primary: '#E8590C',
  primaryHover: '#F3752B',
  primaryActive: '#C94A09',
  accent: '#2F9E44',
  bgLayout: '#FBF7F2',
  bgContainer: '#FFFFFF',
  textHeading: '#2B2118',
};

/**
 * @name ProLayout shell configuration
 */
const Settings: ProLayoutProps & {
  pwa?: boolean;
  logo?: string;
} = {
  navTheme: 'light',
  colorPrimary: brand.primary,
  layout: 'top',
  splitMenus: false,
  contentWidth: 'Fluid',
  fixedHeader: true,
  fixSiderbar: true,
  colorWeak: false,
  title: 'Your Recipe',
  pwa: false,
  logo: '/logo.svg',
  iconfontUrl: '',
  token: {
    header: {
      colorBgHeader: '#FFFFFF',
      colorHeaderTitle: brand.textHeading,
      colorTextMenu: '#5B5044',
      colorTextMenuSecondary: '#8A7F70',
      colorTextMenuSelected: brand.primary,
      colorBgMenuItemSelected: 'rgba(232, 89, 12, 0.08)',
      colorTextMenuActive: brand.primary,
      colorTextRightActionsItem: '#5B5044',
      heightLayoutHeader: 64,
    },
    sider: {
      colorMenuBackground: '#FFFFFF',
    },
    pageContainer: {
      colorBgPageContainer: brand.bgLayout,
    },
  },
};

export default Settings;
