function CashierHandler(){
    return {
        ModalCloseCashier:false,
        withdrawal:false,
        withdrawalValue:Number(),
        referenceMonth:null,
        ValueCashier:Number(),
        totalCashier:Number(),
        entries:true,
        exits:true,



    startclosecashier(){
        const date = new Date()
        this.referenceMonth= date.toLocaleDateString('pt-BR', {day:'2-digit', month: 'long', year: 'numeric' });
        this.ModalCloseCashier = true;
    },
    flowclosecashier(){
        this.ValueCashier = PaymentFlow.parseNumber(this.ValueCashier);
        if(this.withdrawal){
            this.withdrawalValue = PaymentFlow.parseNumber(this.withdrawalValue);
            this.totalCashier = this.ValueCashier - this.withdrawalValue;
            if(this.totalCashier < 0){
                notificationModal.show({
                    title:'Erro ao fechar caixa',
                    message:'O valor do caixa não pode ser negativo!'
                })
            }else{
                this.ModalCloseCashier = false;
                // Logica da API para fechar o caixa
                const payload = {
                    'withdrawalValue':this.withdrawalValue,
                    'closing_balance':this.totalCashier,
                    'action':'update'
                }
                this.send_request(payload);
            }
        }else{
            this.ModalCloseCashier = false;
            this.totalCashier = this.ValueCashier;
            // logica da API para fechar o caixa
            const payload = {
                    'withdrawalValue':this.withdrawalValue,
                    'closing_balance':this.totalCashier,
                    'action':'update'
                }
            this.send_request(payload);
        }
    },
    send_request(payload){
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch('', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(payload),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
               if (data.status !== 'success'){
                notificationModal.show({
                    title:data.title,
                    message:data.message
                })
               } else {
                notificationModal.show({
                    title:data.title,
                    message:data.message,
                    onPrimary: () => { window.location.reload(); }
                })
               }
            })
            .catch((error) => {
                console.error('Error:', error);
            });

    },
    openCashier(){
        const payload = {
            'action':'create'
        }
        this.send_request(payload);
    },

}
}
