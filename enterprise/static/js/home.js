function mainPage() {
  return {
    formData: {},
    'dropdown': false,
    'alert': false,
    'registerModal': false,
     payments: [],
     validate:false,
     plan_price: '',
     total:Number(),
     value_after_discount: '',
     value_after_discount_numeric:'',
     discount_value:Number(),
     percent_discount:Number(),
     tot:0,
     
    addPayment(id, method){
      this.payments.push({
        id:id,
        method: method,
        installments: '1',
      }),
      this.$nextTick(() => {
        lucide.createIcons();
      });
      this.dropdown = false
      
      },
      removePayment(id){
      this.payments.splice(id, 1)
      this.$nextTick(() => {
        lucide.createIcons();
        this.validate_value();
      })
      },

      validate_value(){
        var message = document.getElementById('validate_message')
        let total = 0
        this.payments.forEach(p => {
          total += Number(p.receive_value)
        });
        this.tot = total
        if (this.tot != 0){
          diference = Number(this.paymentModal.feeData.final_amount) - Number(this.tot)
          var button = document.getElementById('button-confirm')
            message.innerHTML = this.tot < this.paymentModal.feeData.final_amount ? `<p>Valor parcial recebido.</p> <p>Restam ${diference.toLocaleString('pt-BR', {style: 'currency', currency:'BRL'})} a serem pagos.</p>` : ''
            this.alert = this.tot < this.paymentModal.feeData.final_amount ? true : false
            this.validate = this.tot < this.paymentModal.feeData.final_amount ? false : true

          }
        else {
          this.alert = false
        }
        
      },

    recalcTotal() {
      let total = this.paymentModal.feeData.base_amount|| 0;
      if (this.formData.apply_discount) {
        if (this.formData.percent_discount) {
          total -= total * (this.formData.percent_discount / 100);
        }
        if (this.formData.value_discount) {
          total -= Number(this.formData.value_discount);
        }
        if (this.formData.percent_fine) {
          total += total * (this.formData.percent_fine / 100);
        }
        if (this.formData.value_fine) {
          total += Number(this.formData.value_fine);
        }
      }
      this.paymentModal.feeData.final_amount = total.toFixed(2);
    },



    paymentModal: {
      open: false,
      monthlyfeeId: null,
      counterElementId: null,
      feeData: {
        student_name:'',
        plan: '',
        base_amount: 0,
        final_amount: 0,
        reference_month:'',
        discount_percent: 0,
        discount_value: 0,
        payment_methods: [],
        quantity_installments: '1x',
        current_payment_method: null,
      },

      async show(id, counterElementId) {
        this.open = true;
        this.monthlyfeeId = id;
        this.counterElementId = counterElementId;
        

        const res = await fetch(`students/api/monthlyfee/${id}/`);
        if (!res.ok) {
          console.error('Erro ao carregar dados do pagamento');
          return;
        }
        
        const data = await res.json();
        this.feeData.student_name = data.student_name
        this.feeData.plan = data.plan ?? '';
        this.feeData.base_amount = this.parseNumber(data.base_amount);
        this.feeData.reference_month = data.reference_month
        this.feeData.discount_percent = this.parseNumber(data.discount_percent);
        this.feeData.discount_value = this.parseNumber(data.discount_value);
        this.feeData.final_amount = this.parseNumber(data.final_amount || data.base_amount);
        this.feeData.quantity_installments = data.quantity_installments ? `${data.quantity_installments}x` : '1x';

        this.selectedMethod = this.resolveSelectedMethod(data.current_payment_method);
        if (!this.selectedMethod && this.feeData.payment_methods.length) {
          this.selectedMethod = this.feeData.payment_methods[0].id;
        }
        this.updateFromPercent();
      },

      close() {
        this.open = false;
        this.monthlyfeeId = null;
        this.counterElementId = null;
        this.feeData = {
          plan: '',
          base_amount: 0,
          final_amount: 0,
          discount_percent: 0,
          discount_value: 0,
          quantity_installments: '1x',
        };
      },

      updateFromPercent() {
        const base = this.parseNumber(this.feeData.base_amount);
        let percent = this.parseNumber(this.feeData.discount_percent);
        if (percent < 0) percent = 0;
        if (percent > 100) percent = 100;
        this.feeData.discount_percent = percent;

        const discount = this.round(base * (percent / 100));
        this.feeData.discount_value = discount;
        this.feeData.final_amount = this.round(base - discount);
      },

      updateFromValue() {
        const base = this.parseNumber(this.feeData.base_amount);
        let discount = this.parseNumber(this.feeData.discount_value);
        if (discount < 0) discount = 0;
        if (discount > base) discount = base;
        this.feeData.discount_value = discount;

        const percent = base === 0 ? 0 : this.round((discount / base) * 100);
        this.feeData.discount_percent = percent;
        this.feeData.final_amount = this.round(base - discount);
      },

      parseNumber(value) {
        const num = typeof value === 'string' ? value.replace(',', '.') : value;
        const parsed = Number.parseFloat(num);
        return Number.isFinite(parsed) ? parsed : 0;
      },

      round(value) {
        return Number((Math.round((value + Number.EPSILON) * 100) / 100).toFixed(2));
      },

      normalizedInstallments() {
        const raw = this.feeData.quantity_installments;
        if (!raw) return null;
        const normalized = String(raw).toLowerCase().replace('x', '').trim();
        if (normalized === '') return null;
        const value = Number.parseInt(normalized, 10);
        return Number.isNaN(value) || value <= 0 ? null : value;
      },

      formatDecimal(value) {
        return this.round(this.parseNumber(value)).toFixed(2);
      },

      submitForm() {
        const container = document.getElementById("mainContainer");
        const updateUrl = container.dataset.updateUrl;
        const csrf = container.dataset.csrf;

        const payload = {
          discount_percent: this.formatDecimal(this.feeData.discount_percent),
          discount_value: this.formatDecimal(this.feeData.discount_value),
          final_amount: this.formatDecimal(this.feeData.final_amount),
        };

        const installments = this.normalizedInstallments();
        if (installments) {
          payload.quantity_installments = installments;
        }

        fetch(updateUrl, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrf,
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            if (this.counterElementId) {
              const counter = document.getElementById(this.counterElementId);
              if (counter) {
                const currentValue = Number.parseInt(counter.textContent, 10) || 0;
                counter.textContent = Math.max(0, currentValue - 1);
              }
            }
            document.querySelector(`#fee-row-${this.monthlyfeeId}`).remove();
            this.close();
          } else if (data.errors) {
            const errorMessages = Object.values(data.errors).flat().join('\n');
            alert(errorMessages || 'Não foi possível processar o pagamento.');
          } else {
            alert(data.message || 'Não foi possível processar o pagamento.');
          }
        })
        .catch(() => {
          alert('Erro inesperado ao enviar os dados do pagamento.');
        });
      }
    },
    deactivateModal: {
      open: false,
      feeId: null,
      studentId: null,
      counterElementId: null,
      rowSelector: null,
      reason: '',
      error: null,

      show({ feeId, studentId, counterId }) {
        this.open = true;
        this.error = null;
        this.reason = '';
        this.feeId = feeId;
        this.studentId = studentId;
        this.counterElementId = counterId;
        this.rowSelector = `#fee-row-${feeId}`;
      },

      close() {
        this.open = false;
        this.feeId = null;
        this.studentId = null;
        this.counterElementId = null;
        this.rowSelector = null;
        this.reason = '';
        this.error = null;
      },

      extractError(errors) {
        if (!errors) {
          return null;
        }
        if (Array.isArray(errors)) {
          return errors.join(' ');
        }
        const first = Object.values(errors)[0];
        if (Array.isArray(first)) {
          return first.join(' ');
        }
        if (typeof first === 'string') {
          return first;
        }
        return null;
      },

      submit() {
        const reasonText = (this.reason || '').trim();
        if (!reasonText) {
          this.reason = '';
          this.error = 'Informe o motivo da inativação.';
          return;
        }

        this.reason = reasonText;

        const container = document.getElementById('mainContainer');
        const url = container.dataset.inactivateUrl;
        const csrf = container.dataset.csrf;

        this.error = null;

        fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrf,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            student_id: this.studentId,
            reason: reasonText,
          }),
        })
          .then((res) => res.json())
          .then((data) => {
            if (data.success) {
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
              alert(message);
            } else {
              this.error = this.extractError(data.errors) || data.message || 'Não foi possível inativar o aluno.';
            }
          })
          .catch(() => {
            this.error = 'Erro inesperado ao enviar os dados.';
          });
      },
    }
  }
}
function calendar() {
  return {
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear(),
    monthNames: ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"],
    events: [],
    accountsUrl: "",
    eventDates: new Set(),
    init() {
      const container = document.getElementById("calendarContainer");
       try {
            this.events = JSON.parse(container.dataset.events || "[]");
        } catch (e) {
            console.error("Erro ao fazer parse dos eventos:", e, container.dataset.events);
            this.events = [];
        }
      this.accountsUrl = container.dataset.accountsUrl;
      this.eventDates = new Set(this.events.map(event => event.date));
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
    }
  }
}
