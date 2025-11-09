function nfeHandler() {
  return {
    selected: [],
    description: "",
    reference_month: "",
    plan_filter: 'Todos',
    student_filter: '',
    rows: [],
    showModalEmitir: false,

    init() {
      this.rows = Array.from(this.$el.querySelectorAll('[data-nfe-row]'));
      this.$watch('reference_month', () => this.applyFilters());
      this.$watch('plan_filter', () => this.applyFilters());
      this.$watch('student_filter', () => this.applyFilters());
      this.applyFilters();
    },

    get total() {
      return this.selected.reduce((acc, item) => acc + item.valor, 0);
    },
    get tot_select(){
        return this.selected.length
    },

    toggleSelected(el, id, name, cpf, valor) {
      const numericValue = typeof valor === 'number' ? valor : parseFloat(valor) || 0;
      if (el.checked) {
        if (!this.selected.some(s => s.id === id)) {
          this.selected.push({id, name, cpf, valor: numericValue});
        }
      } else {
        this.selected = this.selected.filter(s => s.id !== id);
      }
    },

    setPlanFilter(filter) {
      this.plan_filter = filter;
    },

    clearFilters() {
      this.plan_filter = 'Todos';
      this.student_filter = '';
      this.reference_month = '';
      this.applyFilters();
    },

    applyFilters() {
      if (!this.rows.length) {
        this.rows = Array.from(this.$el.querySelectorAll('[data-nfe-row]'));
      }
      const planFilter = (this.plan_filter || '').toLowerCase();
      const studentFilter = (this.student_filter || '').trim().toLowerCase();
      const monthFilter = this.reference_month;

      this.rows.forEach(row => {
        const rowPlan = (row.dataset.plan || '').toLowerCase();
        const rowStudent = (row.dataset.student || '').toLowerCase();
        const rowMonth = row.dataset.month || '';

        const matchesPlan = !planFilter || planFilter === 'todos' || rowPlan.includes(planFilter);
        const matchesStudent = !studentFilter || rowStudent.includes(studentFilter);
        const matchesMonth = !monthFilter || rowMonth === monthFilter;

        if (matchesPlan && matchesStudent && matchesMonth) {
          row.classList.remove('hidden');
        } else {
          row.classList.add('hidden');
        }
      });
    },

    openModalEmitir() {
      if (this.reference_month.length === 0) {
        window.notificationModal.show({
          title: 'Selecione o mês de referência',
          message: 'Informe o mês de competência antes de continuar.',
        });
        return;
      } else if (this.selected.length === 0) {
        window.notificationModal.show({
          title: 'Selecione alunos',
          message: 'Escolha ao menos um aluno para emitir a nota.',
        });
        return;
      }
      this.showModalEmitir = true;
    },

    async emitir() {
      let payload = {
        student: this.selected,
        description: this.description,
        reference_month: this.reference_month
      };
      if (this.description.length === 0){
        window.notificationModal.show({
          title: 'Descrição obrigatória',
          message: 'Preencha a descrição da nota fiscal.',
        });
        return;
      }
      else {
        try {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
        let response = await fetch("/nfe_api", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify(payload)
        });

        if (response.ok) {
          this.showModalEmitir = false;
          window.notificationModal.show({
            title: 'Solicitação enviada',
            message: 'Solicitação de emissão enviada com sucesso!',
            primaryLabel: 'Atualizar página',
            onPrimary: () => window.location.reload(),
          });

        } else {
            const data = await response.json().catch(() => ({}));
            const msg = data.message || JSON.stringify(data) || 'Erro ao enviar a solicitação.';
            window.notificationModal.show({
              title: 'Não foi possível concluir',
              message: msg,
            });

        }
      } catch (err) {
        console.error(err);
        window.notificationModal.show({
          title: 'Erro de conexão',
          message: 'Não foi possível enviar a solicitação de emissão.',
        });
      }
      }
    }
  }
}
