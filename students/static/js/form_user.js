function formHandler(){
    const containerMain = document.getElementById('containerMain');
    let plansData= []
    try {
        plansData = JSON.parse(containerMain.dataset.plans || "[]");
      } catch (e) {
        console.error("Erro ao fazer parse dos planos:", e);
        plansData = [];
      }
    const registrationFee = Number(document.getElementById('registration fee').value)
  return {
    'dropdown': false,
    'alert': false,
     payments: [],
     validate:false,
     plan_price: '',
     total:Number(),
     value_after_discount: '',
     value_after_discount_numeric:'',
     discount_value:Number(),
     percent_discount:Number(),
     tot:0,


    completeValue(event){
      var plan_id = event.target.value;
      var planselected = plansData.find(p => p.id == plan_id)
      this.plan_price = Number(planselected['price']).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
      this.total = Number(planselected['price']) + registrationFee
      this.value_after_discount = this.total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
      this.value_after_discount_numeric = this.total
      this.$nextTick(()=>{
        this.validate_value()
      })
    },

    recalctotal(){
      if(this.discount_value){
        var calc = this.total - Number(this.discount_value)
        this.value_after_discount = calc.toLocaleString('pt-BR', {style:'currency', currency:'BRL'})
        this.value_after_discount_numeric = Number(calc)
      }
      else if(this.percent_discount){
        var calc = this.total - (this.percent_discount / 100 * this.total)
        this.value_after_discount = calc.toLocaleString('pt-BR', {style: 'currency', currency:'BRL'})
        this.value_after_discount_numeric = Number(calc)
      } else {
        this.value_after_discount = this.total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
        this.value_after_discount_numeric = Number(this.total)
      }

    },

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
        message.innerHTML = this.tot < this.value_after_discount_numeric ? `<p>Valor parcial recebido.</p> <p>Restam R$${this.value_after_discount_numeric - this.tot} a serem pagos.</p>` : ''
        this.alert = this.tot < this.value_after_discount_numeric ? true : false
        this.validate = this.tot < this.value_after_discount_numeric ? false : true
        }else {
          this.alert = false
        }
        
      }
      
    }
}

 