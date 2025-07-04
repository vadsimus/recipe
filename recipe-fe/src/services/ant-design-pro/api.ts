// @ts-ignore
/* eslint-disable */
import { request } from '@umijs/max';

/** 获取当前的用户 GET /api/currentUser */
export async function currentUser(options?: { [key: string]: any }) {
  const token = localStorage.getItem('access_token');
  const resp = await request<{
    data: API.CurrentUser;
  }>('/api/currentUser/', {
    method: 'GET',
    headers: {
      Authorization: token ? `Bearer ${token}` : '',
      // ...options?.headers,
    },
    // ...(options || {}),
  });
  return resp.data
}

export async function fetchData(options?: { [key: string]: any }) {
  const token = localStorage.getItem('access_token');
  const resp = await request<{
    data: API.CurrentUser;
  }>(options?.endpoint, {
    method: 'GET',
    headers: {
      Authorization: token ? `Bearer ${token}` : '',
      ...options?.headers,
    },
    ...(options || {}),
  });
  return resp
}

export async function postData<T = any>(options: {
  endpoint: string;
  data?: any;
  headers?: { [key: string]: any };
}) {
  const token = localStorage.getItem('access_token');
  const resp = await request<T>(options.endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : '',
      ...options.headers,
    },
    data: options.data,
  });
  return resp;
}

export async function deleteData<T = any>(options: {
  endpoint: string;
  headers?: { [key: string]: any };
}) {
  const token = localStorage.getItem('access_token');
  const resp = await request<T>(options.endpoint, {
    method: 'DELETE',
    headers: {
      Authorization: token ? `Bearer ${token}` : '',
      ...options.headers,
    },
  });
  return resp;
}

export async function putData<T = any>(options: {
  endpoint: string;
  data?: any;
  headers?: { [key: string]: any };
}) {
  const token = localStorage.getItem('access_token');
  const resp = await request<T>(options.endpoint, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: token ? `Bearer ${token}` : '',
      ...options.headers,
    },
    data: options.data,
  });
  return resp;
}

/** 退出登录接口 POST /api/login/outLogin */
export async function outLogin(options?: { [key: string]: any }) {
  return request<Record<string, any>>('/api/login/outLogin', {
    method: 'POST',
    ...(options || {}),
  });
}

/** 登录接口 POST /api/login/account */
export async function login(body: API.LoginParams, options?: { [key: string]: any }) {
  return request<API.LoginResult>('/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data: body,
    ...(options || {}),
  });
}

/** 此处后端没有提供注释 GET /api/notices */
export async function getNotices(options?: { [key: string]: any }) {
  return request<API.NoticeIconList>('/api/notices', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取规则列表 GET /api/rule */
export async function rule(
  params: {
    // query
    /** 当前的页码 */
    current?: number;
    /** 页面的容量 */
    pageSize?: number;
  },
  options?: { [key: string]: any },
) {
  return request<API.RuleList>('/api/rule', {
    method: 'GET',
    params: {
      ...params,
    },
    ...(options || {}),
  });
}

/** 更新规则 PUT /api/rule */
export async function updateRule(options?: { [key: string]: any }) {
  return request<API.RuleListItem>('/api/rule', {
    method: 'POST',
    data: {
      method: 'update',
      ...(options || {}),
    },
  });
}

/** 新建规则 POST /api/rule */
export async function addRule(options?: { [key: string]: any }) {
  return request<API.RuleListItem>('/api/rule', {
    method: 'POST',
    data: {
      method: 'post',
      ...(options || {}),
    },
  });
}

/** 删除规则 DELETE /api/rule */
export async function removeRule(options?: { [key: string]: any }) {
  return request<Record<string, any>>('/api/rule', {
    method: 'POST',
    data: {
      method: 'delete',
      ...(options || {}),
    },
  });
}
