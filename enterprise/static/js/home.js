function mainPage() {
  return {
    openDeactivateModal: false,
    monthly_feesID: null,
    paymentModal: {
      open: false,
      monthlyfeeId: null,
      feeData: { plan: '', value: '', },
      paymentMethods: '',
      selectedMethod: null,
      cardchange:null,

      async show(id, cardchange) {
        this.open = true;
        this.monthlyfeeId = id;
        this.cardchange = cardchange
        const res = await fetch(`/api/monthlyfee/${id}/`);
        const data = await res.json();
        if (data.paymentMethods) {
        data.paymentMethods = data.paymentMethods.map(item => ({
            id: item[0],
            name: item[1]
        }));
        this.feeData = data;
    }
      },

      close() {
        this.open = false;
        this.monthlyfeeId = null;
        this.selectedMethod = null;
      },

      submitForm() {
        const container = document.getElementById("mainContainer");
        const updateUrl = container.dataset.updateUrl;
        const csrf = container.dataset.csrf;

        fetch(updateUrl, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrf,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            monthlyfee_id: this.monthlyfeeId,
            payment_method: this.selectedMethod
          })
        })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            let el_total = document.getElementById(this.cardchange.id);
            el_total.innerHTML = parseInt(el_total.textContent, 10) - 1;
            document.querySelector(`#fee-row-${this.monthlyfeeId}`).remove();
            this.close();
            
          } else {
            alert(data.message);
          }
        });
      }
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



