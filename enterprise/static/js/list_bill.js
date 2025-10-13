function modalHandler() {
  const flow = window.PaymentFlow.createPaymentFlow();
  const baseSetPaymentData = flow.setPaymentData;
  const baseUpdateDiscountFromPercent = flow.updateDiscountFromPercent;
  const baseUpdateDiscountFromValue = flow.updateDiscountFromValue;
  const baseUpdateFinePercent = flow.updateFinePercent;
  const baseUpdateFineValue = flow.updateFineValue;
  const baseApplyDiscountEnabled = flow.applyDiscountEnabled;
  const baseRecalculateFinalAmount = flow.recalculateFinalAmount;

  return {
    ...flow,
    showModal: false,
    showStatus: false,
    showDelete: false,
    formData: { payment_method: null },
    mode: '',
    selectedID: null,
    openPaymentDropdown: false,

    syncTotals() {
      this.formData.apply_discount = this.discountEnabled;
      this.formData.percent_discount = this.paymentData.discountPercent;
      this.formData.value_discount = this.paymentData.discountValue;
      this.formData.percent_fine = this.paymentData.finePercent;
      this.formData.value_fine = this.paymentData.fineValue;
      this.formData.total_value = this.formatDecimal(this.paymentData.finalAmount);
    },

    setPaymentData(partial = {}) {
      baseSetPaymentData.call(this, partial);
      this.syncTotals();
    },

    updateDiscountFromPercent(value) {
      baseUpdateDiscountFromPercent.call(this, value);
      this.syncTotals();
    },

    updateDiscountFromValue(value) {
      baseUpdateDiscountFromValue.call(this, value);
      this.syncTotals();
    },

    updateFinePercent(value) {
      baseUpdateFinePercent.call(this, value);
      this.syncTotals();
    },

    updateFineValue(value) {
      baseUpdateFineValue.call(this, value);
      this.syncTotals();
    },

    applyDiscountEnabled(enabled) {
      baseApplyDiscountEnabled.call(this, enabled);
      this.syncTotals();
    },

    recalculateFinalAmount() {
      baseRecalculateFinalAmount.call(this);
      this.syncTotals();
    },

    handleBaseValueChange(value) {
      this.formData.value = value;
      this.setPaymentData({ baseAmount: value });
    },

    modalcreate() {
      this.mode = 'create';
      this.formData = {
        description: '',
        value: '',
        due_date: '',
        appellant: false,
        apply_discount: false,
        payment_method: null,
        status: null,
        percent_discount: 0,
        value_discount: 0,
        percent_fine: 0,
        value_fine: 0,
        total_value: 0,
      };
      this.resetPaymentFlow();
      this.applyDiscountEnabled(false);
      this.showModal = true;
    },

    async modalupdate(id) {
      const res = await fetch(`/bill/api/v1/${id}/`);
      const data = await res.json();
      this.formData = data;
      this.mode = 'update';
      this.selectedID = id;
      this.showModal = true;
      this.setPaymentData({
        baseAmount: data.value,
        finalAmount: data.total_value ?? data.value,
        discountPercent: data.percent_discount ?? 0,
        discountValue: data.value_discount ?? 0,
        finePercent: data.percent_fine ?? 0,
        fineValue: data.value_fine ?? 0,
      });
      this.applyDiscountEnabled(Boolean(data.apply_discount));
      this.syncTotals();
    },

    async modalstatus(id) {
      const res = await fetch(`/bill/api/v1/${id}/`);
      const data = await res.json();
      this.formData = data;
      this.mode = 'update';
      this.selectedID = id;
      this.showStatus = true;
      this.setPaymentData({
        baseAmount: data.value,
        finalAmount: data.total_value ?? data.value,
        discountPercent: data.percent_discount ?? 0,
        discountValue: data.value_discount ?? 0,
        finePercent: data.percent_fine ?? 0,
        fineValue: data.value_fine ?? 0,
      });
      this.applyDiscountEnabled(Boolean(data.apply_discount));
      this.syncTotals();
    },

    async modaldelete(target) {
      const rawId = target && typeof target === 'object' ? target.id : target;
      const id = Number(rawId);
      if (!Number.isFinite(id)) {
        console.error('Identificador de conta inválido:', rawId);
        return;
      }

      this.mode = 'delete';
      this.selectedID = id;
      this.formData = {
        description: target && typeof target === 'object' ? target.description : '',
      };

      try {
        const res = await fetch(`/bill/api/v1/${id}/`);
        if (!res.ok) {
          throw new Error(`Falha ao carregar conta ${id}: ${res.status}`);
        }
        this.formData = await res.json();
      } catch (error) {
        console.error(error);
        this.formData.id = id;
      }

      this.showDelete = true;
    },

    modalclose() {
      this.showModal = false;
      this.showStatus = false;
      this.showDelete = false;
    },

    async submitForm() {
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const header = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      };

      this.syncTotals();

      if (this.mode === 'create') {
        await fetch('/bill/api/v1/', {
          method: 'POST',
          headers: header,
          body: JSON.stringify(this.formData),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
          });
      } else if (this.mode === 'delete') {
        await fetch(`/bill/api/v1/${this.selectedID}/`, {
          method: 'DELETE',
          headers: header,
        });
      } else {
        await fetch(`/bill/api/v1/${this.selectedID}/`, {
          method: 'PUT',
          headers: header,
          body: JSON.stringify(this.formData),
        });
      }
      this.showModal = false;
      this.showStatus = false;
      this.showDelete = false;
      window.location.reload();
    },
  };
}
