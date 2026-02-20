export type Currency = 'RUB' | 'EUR';

const STORAGE_KEY = 'storyqr_currency';

export function getCurrencyPreference(): Currency {
  if (typeof window === 'undefined') return 'RUB';
  const value = window.localStorage.getItem(STORAGE_KEY);
  return value === 'EUR' ? 'EUR' : 'RUB';
}

export function saveCurrencyPreference(currency: Currency) {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, currency);
  }
}

export function getPriceInCurrency(
  price: { rub: number; eur: number },
  currency: Currency
): number {
  return currency === 'EUR' ? price.eur : price.rub;
}

export function formatPriceWithCurrency(
  price: { rub: number; eur: number },
  currency: Currency
): string {
  const amount = getPriceInCurrency(price, currency);
  return new Intl.NumberFormat(currency === 'EUR' ? 'de-DE' : 'ru-RU', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}
