const buildQuery = (params?: Record<string, unknown>) => {
  if (!params) return '';
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
};

export const endpoints = {
  health: () => '/health',
  auth: {
    login: () => '/auth/login',
    register: () => '/auth/register',
    refresh: () => '/auth/refresh',
    me: () => '/auth/me',
    resetPassword: () => '/auth/reset-password',
  },
  albums: {
    list: (params?: Record<string, unknown>) => `/album/albums${buildQuery(params)}`,
    create: () => '/album/albums',
    get: (albumId: string) => `/album/albums/${albumId}`,
    delete: (albumId: string) => `/album/albums/${albumId}`,
    pages: (albumId: string) => `/album/albums/${albumId}/pages`,
    createPage: (albumId: string) => `/album/albums/${albumId}/pages`,
  },
  pages: {
    get: (pageId: string) => `/album/pages/${pageId}`,
    update: (pageId: string) => `/album/pages/${pageId}`,
    delete: (pageId: string) => `/album/pages/${pageId}`,
    media: (pageId: string) => `/media/pages/${pageId}/media`,
    public: (pageId: string) => `/album/public/pages/${pageId}`,
    validatePin: (pageId: string) => `/album/public/pages/${pageId}/pin`,
  },
  media: {
    upload: () => '/media/upload',
    attach: (mediaId: string) => `/media/files/${mediaId}/attach`,
  },
  qr: {
    get: (pageId: string) => `/qr/pages/${pageId}`,
    generate: () => '/qr/generate',
    image: (qrId: string, params?: { format?: 'png' | 'svg' }) =>
      `/qr/${qrId}/image${buildQuery(params)}`,
  },
  analytics: {
    overview: () => '/analytics/overview',
  },
  billing: {
    plans: () => '/billing/plans',
  },
  trial: {
    start: () => '/billing/trial/start',
  },
  orders: {
    create: () => '/billing/orders',
  },
  print: {
    skus: () => '/print/skus',
    jobs: () => '/print/jobs',
  },
};
