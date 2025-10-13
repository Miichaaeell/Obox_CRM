function formHandler() {
  const containerMain = document.getElementById('containerMain');
  let plansData = [];
  try {
    plansData = JSON.parse(containerMain.dataset.plans || '[]');
  } catch (e) {
    console.error('Erro ao fazer parse dos planos:', e);
    plansData = [];
  }

  const registrationFeeField = document.getElementById('registration_fee');
  const registrationFee = registrationFeeField
    ? window.PaymentFlow.parseNumber(registrationFeeField.value)
    : 0;

  const paymentFlow = window.PaymentFlow.createPaymentFlow();

  return {
    ...paymentFlow,
    plans: plansData,
    registrationFee,
    selectedPlanId: null,
    planPrice: 0,

    init() {
      this.applyDiscountEnabled(true);
      const planSelect = this.$el.querySelector('select[name="plan"]');
      if (planSelect) {
        this.completeValue({ target: planSelect });
      }
      this.updateValidation();
    },

    completeValue(event) {
      const planId = Number(event.target.value);
      const planSelected = this.plans.find((plan) => Number(plan.id) === planId);
      const planLabel = event.target.options?.[event.target.selectedIndex]?.text || '';

      if (!planSelected) {
        this.selectedPlanId = null;
        this.planPrice = 0;
        this.setPaymentData({
          planName: planLabel,
          baseAmount: 0,
          reference: '',
        });
        return;
      }

      const planPrice = Number(planSelected.price) || 0;
      const total = planPrice + this.registrationFee;

      this.selectedPlanId = planId;
      this.planPrice = planPrice;
      this.setPaymentData({
        planName: planLabel,
        baseAmount: total,
        reference: '',
      });
      this.payments = [];
      this.updateValidation();
    },

    handlePercentDiscount(value) {
      this.updateDiscountFromPercent(value);
    },

    handleDiscountValue(value) {
      this.updateDiscountFromValue(value);
    },

    handleFinePercent(value) {
      this.updateFinePercent(value);
    },

    handleFineValue(value) {
      this.updateFineValue(value);
    },

    formattedPlanPrice() {
      return this.formatCurrency(this.planPrice);
    },

    formattedRegistrationFee() {
      return this.formatCurrency(this.registrationFee);
    },
  };
}
