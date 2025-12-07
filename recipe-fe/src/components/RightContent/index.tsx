import { QuestionCircleOutlined } from '@ant-design/icons';
import { setLocale, getLocale } from '@umijs/max';
import React, { useState } from 'react';
import { Dropdown } from 'antd';
import type { MenuProps } from 'antd';

export type SiderTheme = 'light' | 'dark';

const langConfig: Record<string, { label: string; icon: string }> = {
  'en-US': {
    label: 'English',
    icon: '🇺🇸',
  },
  'ru-RU': {
    label: 'Русский',
    icon: '🇷🇺',
  },
};

export const SelectLang = () => {
  const [selectedLang, setSelectedLang] = useState(() => {
    const current = getLocale();
    // If current locale is not en-US or ru-RU, default to en-US
    return current === 'ru-RU' ? 'ru-RU' : 'en-US';
  });

  const handleLangChange: MenuProps['onClick'] = ({ key }) => {
    const lang = key as string;
    setLocale(lang, true);
    setSelectedLang(lang);
  };

  // Filter to only show en-US and ru-RU
  const availableLocales = ['en-US', 'ru-RU'];

  const menuItems: MenuProps['items'] = availableLocales.map((lang) => ({
    key: lang,
    label: (
      <>
        <span role="img" aria-label={langConfig[lang]?.label || lang} style={{ marginRight: 8 }}>
          {langConfig[lang]?.icon || '🌐'}
        </span>
        {langConfig[lang]?.label || lang}
      </>
    ),
  }));

  return (
    <Dropdown
      menu={{
        selectedKeys: [selectedLang],
        onClick: handleLangChange,
        items: menuItems,
      }}
      placement="bottomRight"
    >
      <span
        style={{
          cursor: 'pointer',
          padding: 12,
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 18,
          verticalAlign: 'middle',
        }}
      >
        <svg
          viewBox="0 0 24 24"
          focusable="false"
          width="1em"
          height="1em"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M0 0h24v24H0z" fill="none" />
          <path
            d="M12.87 15.07l-2.54-2.51.03-.03c1.74-1.94 2.98-4.17 3.71-6.53H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z "
            className="css-c4d79v"
          />
        </svg>
      </span>
    </Dropdown>
  );
};

export const Question = () => {
  return (
    <div
      style={{
        display: 'flex',
        height: 26,
      }}
      onClick={() => {
        window.open('https://pro.ant.design/docs/getting-started');
      }}
    >
      <QuestionCircleOutlined />
    </div>
  );
};
