// https://umijs.org/config/
import { defineConfig } from '@umijs/max';
import { join } from 'path';
import defaultSettings, { brand } from './defaultSettings';
import proxy from './proxy';
import routes from './routes';

const { REACT_APP_ENV = 'dev' } = process.env;

const PUBLIC_PATH: string = '/';

export default defineConfig({
  hash: true,

  publicPath: PUBLIC_PATH,
  routes,
  theme: {
    'root-entry-name': 'variable',
  },
  ignoreMomentLocale: true,
  proxy: {
    '/api/': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      pathRewrite: { '^': '' }, // Remove /api prefix if needed
    },
    '/media/': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
  },
  fastRefresh: true,
  model: {},
  initialState: {},
  title: 'Your Recipe',
  layout: {
    locale: false,
    ...defaultSettings,
  },
  moment2dayjs: {
    preset: 'antd',
    plugins: ['duration'],
  },
  locale: {
    // default zh-CN
    default: 'en-US',
    antd: true,
    // default true, when it is true, will use `navigator.language` overwrite default
    baseNavigator: true,
  },
  antd: {
    theme: {
      token: {
        colorPrimary: brand.primary,
        colorInfo: brand.primary,
        colorSuccess: brand.accent,
        colorLink: brand.primary,
        colorBgLayout: brand.bgLayout,
        borderRadius: 10,
        fontFamily:
          "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      },
      components: {
        Button: {
          controlHeight: 38,
          fontWeight: 500,
        },
        Card: {
          borderRadiusLG: 16,
        },
        Modal: {
          borderRadiusLG: 16,
        },
        Drawer: {
          borderRadiusLG: 16,
        },
        Input: {
          controlHeight: 38,
        },
        Select: {
          controlHeight: 38,
        },
        Layout: {
          headerBg: '#FFFFFF',
        },
      },
    },
  },
  request: {},
  access: {},
  headScripts: [
    { src: join(PUBLIC_PATH, 'scripts/loading.js'), async: true },
  ],
  presets: ['umi-presets-pro'],
  // openAPI: [
  //   {
  //     requestLibPath: "import { request } from '@umijs/max'",
  //     // 或者使用在线的版本
  //     // schemaPath: "https://gw.alipayobjects.com/os/antfincdn/M%24jrzTTYJN/oneapi.json"
  //     schemaPath: join(__dirname, 'oneapi.json'),
  //     mock: false,
  //   },
  //   {
  //     requestLibPath: "import { request } from '@umijs/max'",
  //     schemaPath: 'https://gw.alipayobjects.com/os/antfincdn/CA1dOm%2631B/openapi.json',
  //     projectName: 'swagger',
  //   },
  // ],
  mako: {},
  esbuildMinifyIIFE: true,
  requestRecord: {},
});
