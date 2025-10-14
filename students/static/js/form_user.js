function formHandler() {
  const containerMain = document.getElementById('containerMain');
  let plansData = [];
  let activationUrl = '';

  try {
    plansData = JSON.parse(containerMain?.dataset?.plans || '[]');
  } catch (e) {
    console.error('Erro ao fazer parse dos planos:', e);
    plansData = [];
  }

  if (containerMain?.dataset?.activationUrl) {
    activationUrl = containerMain.dataset.activationUrl;
  }

  const registrationFeeField = document.getElementById('registration_fee');
  const registrationFee = registrationFeeField
    ? window.PaymentFlow.parseNumber(registrationFeeField.value)
    : 0;

  const paymentFlow = window.PaymentFlow.createPaymentFlow();

  return {
    ...paymentFlow,
    plans: plansData,
    activationUrl,
    registrationFee,
    selectedPlanId: null,
    planPrice: 0,
    isSubmitting: false,
    registerModal: false,

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
        this.updateValidation();
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

    prepareActivation() {
      if (this.isSubmitting || !this.validate) {
        return;
      }

      const form = this.$refs?.activationForm;
      if (form) {
        const nameInput = form.querySelector('[name="name"]');
        const planSelect = form.querySelector('select[name="plan"]');
        const now = new Date();
        const reference = `${String(now.getMonth() + 1).padStart(2, '0')}/${now.getFullYear()}`;
        const payerName = nameInput ? (nameInput.value || '') : '';

        this.setPaymentData({
          payerName,
          reference,
        });

        if (planSelect && !planSelect.value) {
          this.completeValue({ target: planSelect });
        }
      }

      this.alert = false;
      this.registerModal = true;
    },

    async submitForm() {
      if (this.isSubmitting) {
        return;
      }

      if (!this.validate || !this.payments.length) {
        this.alert = true;
        this.validationMessage = 'Adicione ao menos um pagamento antes de continuar.';
        return;
      }

      const form = this.$refs?.activationForm;
      if (!form) {
        console.error('Formulário de ativação não encontrado.');
        return;
      }

      const csrfInput = form.querySelector('[name=csrfmiddlewaretoken]');
      const csrf = csrfInput ? csrfInput.value : '';
      const url =
        form.dataset.activationUrl ||
        this.activationUrl ||
        form.closest('#containerMain')?.dataset?.activationUrl ||
        '';

      if (!url) {
        window.notificationModal.show({
          title: 'Não foi possível continuar',
          message: 'Não conseguimos identificar a rota de ativação do aluno.',
          primaryLabel: 'Entendi',
        });
        return;
      }

      const formData = new FormData(form);
      const studentPayload = {
        name: formData.get('name') || '',
        cpf_cnpj: formData.get('cpf_cnpj') || '',
        date_of_birth: formData.get('date_of_birth') || '',
        phone_number: formData.get('phone_number') || '',
        plan: formData.get('plan') || null,
      };

      if (studentPayload.plan !== null) {
        const planId = Number(studentPayload.plan);
        studentPayload.plan = Number.isFinite(planId) ? planId : null;
      }

      if (!studentPayload.date_of_birth) {
        studentPayload.date_of_birth = null;
      }

      const paymentsPayload = this.payments.map((payment) => ({
        payment_method: payment.payment_method,
        value: this.formatDecimal(payment.value),
        quantity_installments: Number(payment.quantity_installments || 1),
      }));

      const payload = {
        student: studentPayload,
        payment: {
          discount_percent: this.formatDecimal(this.paymentData.discountPercent),
          discount_value: this.formatDecimal(this.paymentData.discountValue),
          amount: this.formatDecimal(this.paymentData.finalAmount),
          payments: paymentsPayload,
        },
      };

      this.isSubmitting = true;

     fetch(url, {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         'X-CSRFToken': csrf,
       },
       body: JSON.stringify(payload),
     })
       .then(async (res) => {
         const data = await res.json().catch(() => ({}));
         if (!res.ok) {
           const message =
             data?.message ||
             data?.detail ||
             'Não foi possível processar a ativação do aluno.';
            if (window.notificationModal) {
              window.notificationModal.show({
                title: 'Não foi possível concluir',
                message,
                primaryLabel: 'Entendi',
              });
            }
            throw new Error(message);
         }
         return data;
       })
       .then((data) => {
         this.registerModal = false;
          if (window.notificationModal) {
            window.notificationModal.show({
              title: 'Aluno reativado',
              message: data?.message || 'O aluno foi reativado com sucesso.',
              primaryLabel: 'Atualizar página',
              onPrimary: () => window.location.reload(),
            });
          }
       })
       .catch((error) => {
          console.error(error);
          if (window.notificationModal) {
            window.notificationModal.show({
              title: 'Não foi possível concluir',
              message: error.message || 'Não conseguimos processar a ativação do aluno.',
              primaryLabel: 'Entendi',
            });
          }
       })
       .finally(() => {
         this.isSubmitting = false;
       });
    },
  };
}
