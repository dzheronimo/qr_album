const logEvent = (name: string, payload?: Record<string, unknown>) => {
  if (process.env.NODE_ENV !== 'production') {
    console.info(`[analytics] ${name}`, payload ?? {});
  }
};

export const trackPricingView = async () => logEvent('pricing_view');
export const trackCurrencySwitch = async (from: string, to: string) => logEvent('currency_switch', { from, to });
export const trackPlanSelect = async (planId: string, currency: string) => logEvent('plan_select', { planId, currency });
export const trackTrialStartClick = async () => logEvent('trial_start_click');
export const trackTrialStartSuccess = async () => logEvent('trial_start_success');
export const trackCheckoutOpen = async (planId: string, currency: string) => logEvent('checkout_open', { planId, currency });
export const trackCheckoutAddonChange = async (sku: string, enabled: boolean) => logEvent('checkout_addon_change', { sku, enabled });
export const trackCheckoutPayClick = async (
  planId: string,
  addons: string[],
  amount: number,
  currency: string
) => logEvent('checkout_pay_click', { planId, addons, amount, currency });
export const trackCheckoutPayRedirect = async (paymentUrl: string) => logEvent('checkout_pay_redirect', { paymentUrl });
