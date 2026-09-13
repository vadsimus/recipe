import { login } from '@/services/ant-design-pro/api';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Helmet, history, useIntl, useModel } from '@umijs/max';
import { Alert, Button, Checkbox, Form, Input, message } from 'antd';
import React, { useState } from 'react';
import { flushSync } from 'react-dom';
import Settings from '../../../../config/defaultSettings';

const Login: React.FC = () => {
  const [submitting, setSubmitting] = useState(false);
  const [loginError, setLoginError] = useState(false);
  const { initialState, setInitialState } = useModel('@@initialState');
  const intl = useIntl();

  const fetchUserInfo = async () => {
    const userInfo = await initialState?.fetchUserInfo?.();
    if (userInfo) {
      flushSync(() => {
        setInitialState((s) => ({
          ...s,
          currentUser: userInfo,
        }));
      });
    }
  };

  const handleSubmit = async (values: API.LoginParams) => {
    setLoginError(false);
    setSubmitting(true);
    try {
      const msg = await login(values);
      if (!msg?.access) {
        setLoginError(true);
        return;
      }
      message.success(intl.formatMessage({ id: 'pages.login.success' }));
      localStorage.setItem('access_token', msg.access);
      localStorage.setItem('refresh_token', msg.refresh || '');
      await fetchUserInfo();
      const urlParams = new URL(window.location.href).searchParams;
      history.push(urlParams.get('redirect') || '/');
    } catch (error) {
      setLoginError(true);
      message.error(intl.formatMessage({ id: 'pages.login.failure' }));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
        background:
          'radial-gradient(circle at 15% 20%, rgba(232,89,12,0.14), transparent 45%),' +
          'radial-gradient(circle at 85% 85%, rgba(47,158,68,0.12), transparent 45%),' +
          '#FBF7F2',
      }}
    >
      <Helmet>
        <title>
          {intl.formatMessage({ id: 'menu.login' })}
          {Settings.title && ` - ${Settings.title}`}
        </title>
      </Helmet>

      <div
        style={{
          width: '100%',
          maxWidth: 380,
          background: '#fff',
          borderRadius: 20,
          padding: '40px 36px',
          boxShadow: '0 24px 48px -20px rgba(43, 33, 24, 0.22)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <img src="/logo.svg" alt="Your Recipe" width={52} height={52} style={{ borderRadius: 14 }} />
          <h1 style={{ fontSize: 22, fontWeight: 700, margin: '16px 0 4px', color: '#2B2118' }}>
            {intl.formatMessage({ id: 'pages.login.title' })}
          </h1>
          <p style={{ color: '#8A7F70', fontSize: 14, margin: 0 }}>
            {intl.formatMessage({ id: 'pages.login.subtitle' })}
          </p>
        </div>

        {loginError && (
          <Alert
            style={{ marginBottom: 20, borderRadius: 10 }}
            message={intl.formatMessage({ id: 'pages.login.errorMessage' })}
            type="error"
            showIcon
          />
        )}

        <Form layout="vertical" initialValues={{ autoLogin: true }} onFinish={handleSubmit}>
          <Form.Item
            name="username"
            rules={[{ required: true, message: intl.formatMessage({ id: 'pages.login.username.required' }) }]}
          >
            <Input
              size="large"
              prefix={<UserOutlined style={{ color: '#B8ADA0' }} />}
              placeholder={intl.formatMessage({ id: 'pages.login.username.placeholder' })}
            />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: intl.formatMessage({ id: 'pages.login.password.required' }) }]}
          >
            <Input.Password
              size="large"
              prefix={<LockOutlined style={{ color: '#B8ADA0' }} />}
              placeholder={intl.formatMessage({ id: 'pages.login.password.placeholder' })}
            />
          </Form.Item>
          <Form.Item name="autoLogin" valuePropName="checked" style={{ marginBottom: 20 }}>
            <Checkbox>{intl.formatMessage({ id: 'pages.login.rememberMe' })}</Checkbox>
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Button type="primary" htmlType="submit" size="large" block loading={submitting}>
              {intl.formatMessage({ id: 'pages.login.submit' })}
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};

export default Login;
