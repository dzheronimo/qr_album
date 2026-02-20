import { ApiError } from '@/types';

interface UiAction {
  label: string;
  onClick: () => void;
}

interface UiError {
  title: string;
  message: string;
  display: 'inline' | 'toast';
  actions?: UiAction[];
}

interface MapperActions {
  retryAction?: () => void;
  resetPasswordAction?: () => void;
  checkStatusAction?: () => void;
}

export function mapToUiError(error: unknown, actions: MapperActions = {}): UiError {
  const fallback: UiError = {
    title: 'Ошибка',
    message: 'Что-то пошло не так. Попробуйте снова.',
    display: 'inline',
  };

  if (!(error instanceof Error)) return fallback;

  const status = (error as ApiError).status;

  if (status === 0) {
    return {
      title: 'Проблема с сетью',
      message: 'Проверьте подключение к интернету и повторите попытку.',
      display: 'inline',
      actions: actions.checkStatusAction ? [{ label: 'Статус сервиса', onClick: actions.checkStatusAction }] : undefined,
    };
  }

  if (status === 401) {
    return {
      title: 'Неверные учетные данные',
      message: 'Проверьте email и пароль.',
      display: 'inline',
      actions: actions.resetPasswordAction ? [{ label: 'Сбросить пароль', onClick: actions.resetPasswordAction }] : undefined,
    };
  }

  if (status === 429) {
    return {
      title: 'Слишком много попыток',
      message: 'Подождите немного и попробуйте снова.',
      display: 'toast',
      actions: actions.retryAction ? [{ label: 'Повторить', onClick: actions.retryAction }] : undefined,
    };
  }

  return {
    title: 'Ошибка запроса',
    message: error.message || fallback.message,
    display: status && status >= 500 ? 'toast' : 'inline',
    actions: actions.retryAction ? [{ label: 'Повторить', onClick: actions.retryAction }] : undefined,
  };
}

export function shouldShowToast(error: UiError): boolean {
  return error.display === 'toast';
}

export function shouldShowInlineAlert(error: UiError): boolean {
  return error.display === 'inline';
}

export function logError(error: unknown, context: string) {
  console.error(`[${context}]`, error);
}
