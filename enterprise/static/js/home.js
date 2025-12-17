function mainPage() {
  const paymentFlow = window.PaymentFlow.createPaymentFlow();

  return {
    ...paymentFlow,
    registerModal: false,
    paymentModal: false,
    monthlyfeeId: null,
    counterElementId: null,
    urlApi: '',

    async show(id, counterElementId, urlApi) {
      this.resetPaymentFlow();
      this.paymentModal = true;
      this.monthlyfeeId = id;
      this.counterElementId = counterElementId;
      this.urlApi = urlApi;

      try {
        const res = await fetch(urlApi);
        if (!res.ok) {
          console.error('Erro ao carregar dados do pagamento', res.status);
          return;
        }

        const data = await res.json();

        this.setPaymentData({
          payerName: data.student_name || '',
          planName: data.plan || '',
          reference: data.reference_month || '',
          baseAmount: data.amount,
          finalAmount: data.final_amount ?? data.amount,
          discountPercent: data.discount_percent ?? 0,
          discountValue: data.discount_value ?? 0,
          finePercent: data.fine_percent ?? 0,
          fineValue: data.fine_value ?? 0,
        });

        const hasAdjustments = Boolean(
          this.paymentData.discountPercent ||
          this.paymentData.discountValue ||
          this.paymentData.finePercent ||
          this.paymentData.fineValue,
        );

        this.applyDiscountEnabled(hasAdjustments);
        if (!hasAdjustments) {
          this.recalculateFinalAmount();
        }
      } catch (error) {
        console.error('Erro ao carregar dados do pagamento', error);
      }
    },

    close() {
      this.paymentModal = false;
      this.registerModal = false;
      this.monthlyfeeId = null;
      this.counterElementId = null;
      this.urlApi = '';
      this.resetPaymentFlow();
    },

    submitForm() {
      const container = document.getElementById('mainContainer');
      const csrf = container.dataset.csrf;

      const payload = {
        discount_percent: this.formatDecimal(this.paymentData.discountPercent),
        discount_value: this.formatDecimal(this.paymentData.discountValue),
        amount: this.formatDecimal(this.paymentData.finalAmount),
        payments: this.payments.map(({ payment_method, value, quantity_installments }) => ({
          payment_method,
          value: this.formatDecimal(value),
          quantity_installments,
        })),
      };

      fetch(this.urlApi, {
        method: 'PUT',
        headers: {
          'X-CSRFToken': csrf,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })
        .then(async (res) => {
          const data = await res.json().catch(() => ({}));

          if (!res.ok) {
            console.error('❌ Erro HTTP:', res.status, data);
            let message = 'Não foi possível processar o pagamento.';

            if (data.errors) {
              message = Object.values(data.errors).flat().join('\n');
            } else if (data.detail) {
              message = data.detail;
            } else if (typeof data === 'string') {
              message = data;
            } else if (data.message) {
              message = data.message;
            }

            if (window.notificationModal) {
              window.notificationModal.show({
                title: 'Não foi possível concluir',
                message,
              });
            }

            throw new Error(`HTTP ${res.status}: ${message}`);
          }

          return data;
        })
        .then((data) => {
          if (data.success || data.id || data.amount) {
            if (this.counterElementId) {
              const counter = document.getElementById(this.counterElementId);
              if (counter) {
                const currentValue = Number.parseInt(counter.textContent, 10) || 0;
                counter.textContent = Math.max(0, currentValue - 1);
              }
            }

            const row = document.querySelector(`#fee-row-${this.monthlyfeeId}`);
            if (row) row.remove();

            this.close();
          } else if (window.notificationModal) {
            const msg = data.message || 'O servidor respondeu, mas sem confirmação de sucesso.';
            window.notificationModal.show({
              title: 'Atenção',
              message: msg,
            });
          }
        })
        .catch((err) => {
          console.error('💥 Erro inesperado:', err);
          if (window.notificationModal) {
            window.notificationModal.show({
              title: 'Erro inesperado',
              message: err.message || 'Erro inesperado ao enviar os dados do pagamento.',
            });
          }
        });
    },

    deactivateModal: {
      open: false,
      feeId: null,
      studentId: null,
      counterElementId: null,
      rowSelector: null,
      reason: '',
      error: null,
      url: '',
      statusId: '',

      async show({ feeId, studentId, counterId, url }) {
        this.open = true;
        this.error = null;
        this.reason = '';
        this.feeId = feeId;
        this.studentId = studentId;
        this.counterElementId = counterId;
        this.rowSelector = `#fee-row-${feeId}`;
        this.url = url;
        const res = await fetch('students/status/api/v1/');
        if (!res.ok) {
          console.error('Erro ao carregar dados do pagamento');
          return;
        }
        const data = await res.json();
        const inactive = data.find((status) => status.status.toLowerCase() === 'inativo');
        this.statusId = inactive?.id ?? '';
      },

      close() {
        this.open = false;
        this.feeId = null;
        this.studentId = null;
        this.counterElementId = null;
        this.rowSelector = null;
        this.reason = '';
      },

      submit() {
        const container = document.getElementById('mainContainer');
        const csrf = container.dataset.csrf;
        const payload = {
          observation: this.reason,
          status: this.statusId,
          feeid: this.feeId,
        };

        fetch(this.url, {
          method: 'PATCH',
          headers: {
            'X-CSRFToken': csrf,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        })
          .then(async (res) => {
            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
              console.error('❌ Erro HTTP:', res.status, data);
              let message = 'Não foi possível processar o pagamento.';

              if (data.errors) {
                message = Object.values(data.errors).flat().join('\n');
              } else if (data.detail) {
                message = data.detail;
              } else if (typeof data === 'string') {
                message = data;
              } else if (data.message) {
                message = data.message;
              }

              if (window.notificationModal) {
                window.notificationModal.show({
                  title: 'Não foi possível concluir',
                  message,
                });
              }

              throw new Error(`HTTP ${res.status}: ${message}`);
            }

            return data;
          })
          .then((data) => {
            if (data.success || data.id || data.status) {
              if (this.counterElementId) {
                const counter = document.getElementById(this.counterElementId);
                if (counter) {
                  const currentValue = Number.parseInt(counter.textContent, 10) || 0;
                  counter.textContent = Math.max(0, currentValue - 1);
                }
              }

              if (this.rowSelector) {
                const row = document.querySelector(this.rowSelector);
                if (row) {
                  row.remove();
                }
              }

              const message = data.message || 'Aluno inativado com sucesso.';
              this.close();
              if (window.notificationModal) {
                window.notificationModal.show({
                  title: 'Aluno inativado',
                  message,
                  primaryLabel: 'Ok',
                });
              }
            } else {
              console.log(data);
            }
          })
          .catch((err) => {
            console.log(err);
          });
      },
    },
  };
}

function calendar() {
  return {
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear(),
    monthNames: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'],
    events: [],
    accountsUrl: '',
    eventDates: new Set(),
    init() {
      const container = document.getElementById('calendarContainer');
      try {
        this.events = JSON.parse(container.dataset.events || '[]');
      } catch (e) {
        console.error('Erro ao fazer parse dos eventos:', e, container.dataset.events);
        this.events = [];
      }
      this.accountsUrl = container.dataset.accountsUrl;
      this.eventDates = new Set(this.events.map((event) => event.date));
    },
    get daysInMonth() {
      return new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
    },
    get blanks() {
      return new Date(this.currentYear, this.currentMonth, 1).getDay();
    },
    formatDate(day) {
      const month = String(this.currentMonth + 1).padStart(2, '0');
      const dayFormatted = String(day).padStart(2, '0');
      return `${this.currentYear}-${month}-${dayFormatted}`;
    },
    hasEvent(day) {
      return this.eventDates.has(this.formatDate(day));
    },
    dayClicked(day) {
      if (!this.hasEvent(day)) {
        return;
      }
      const dateParam = this.formatDate(day);
      const separator = this.accountsUrl.includes('?') ? '&' : '?';
      window.location.href = `${this.accountsUrl}${separator}due_date=${dateParam}`;
    },
    prevMonth() {
      if (this.currentMonth === 0) {
        this.currentMonth = 11;
        this.currentYear--;
      } else {
        this.currentMonth--;
      }
    },
    nextMonth() {
      if (this.currentMonth === 11) {
        this.currentMonth = 0;
        this.currentYear++;
      } else {
        this.currentMonth++;
      }
    },
  };
}
