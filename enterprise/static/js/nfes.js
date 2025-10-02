function nfeHandler() {
  return {
    selected: [],
    description: "",
    reference_month: "",
    showModalEmitir: false,
    showModalNotification: false,
    notification: '',

    get total() {
      return this.selected.reduce((acc, item) => acc + item.valor, 0);
    },
    get tot_select(){
        return this.selected.length
    },

    toggleSelected(el, id, valor) {
      if (el.checked) {
        this.selected.push({id, valor});
      } else {
        this.selected = this.selected.filter(s => s.id !== id);
      }
    },

    openModalEmitir() {
      if (this.reference_month.length === 0) {
        this.notification = "Selecione o mês de referência"
        this.showModalNotification =  true;
        return;
      } else if (this.selected.length === 0) {
        this.notification = "Selecione pelo menos 1 aluno"
        this.showModalNotification =  true;
        return;
      }
      this.showModalEmitir = true;
    },

    closeNotification(){
        
        if (this.notification === 'Solicitação de emissão enviada com Sucesso!'){
            this.selected = [];
            this.description = "";
            this.reference_month = "";
            window.location.reload()
        } else {
            this.showModalNotification =  false;
        }
    },

    async emitir() {
      let payload = {
        student: this.selected,
        description: this.description,
        reference_month: this.reference_month
      };
      if (this.description.length === 0){
        this.notification = "Preencha o campo Descrição"
        this.showModalNotification =  true;
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
          this.notification = "Solicitação de emissão enviada com Sucesso!"
          this.showModalNotification =  true;
          
        } else {
            data = await response.json()
            msg = JSON.stringify(data)
            this.notification = msg;
            this.showModalNotification =  true;
          
        }
      } catch (err) {
        console.error(err);
        this.notification = 'Erro de conexão';
        this.showModalNotification =  true;
      }
      }
    }
  }
}

