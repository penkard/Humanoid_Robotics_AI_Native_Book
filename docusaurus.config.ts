import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Built to Think',
  tagline: 'Engineering intelligence that moves through the world',
  favicon: 'img/logo.png',

  future: {
    v4: true,
  },

  // Vercel deployment
  url: 'https://physical-ai-textbook.vercel.app',
  baseUrl: '/',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
    localeConfigs: {
      en: { label: 'English' },
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/docs',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  customFields: {
    // Set CHATBOT_API_URL in Vercel env vars after backend is deployed to Render
    chatbotApiUrl: process.env.CHATBOT_API_URL || 'http://localhost:8000',
  },

  themeConfig: {
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },
    navbar: {
      title: '',
      logo: {
        alt: 'Built to Think logo',
        src: 'img/logo.png',
        style: {height: '28px', width: '28px', objectFit: 'contain'},
      },
      style: 'dark',
      hideOnScroll: false,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'bookSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          label: 'Learn',
          position: 'left',
          to: '/docs/Part-1-introduction/overview',
        },
        {
          href: 'https://github.com/penkard/Humanoid_Robotics_AI_Native_Book',
          label: 'GitHub',
          position: 'right',
        },
        {
          type: 'html',
          position: 'right',
          value: '<a href="/docs/Part-1-introduction/overview" class="navbar__login-btn">Log in</a>',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `© ${new Date().getFullYear()} Physical AI`,
    },
    prism: {
      theme: prismThemes.dracula,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'yaml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
