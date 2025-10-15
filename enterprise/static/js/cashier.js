function CashierHandler(){
    return {
        ModalCloseCashier:false,
        withdrawal:false,
        withdrawalValue:Number(),
        referenceMonth:null,
        ValueCashier:Number(),
        totalCashier:Number(),

    
    startclosecashier(){
        const date = new Date()
        date.setMonth(date.getMonth() - 1)
        this.referenceMonth= date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
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

                notificationModal.show({
                    title:'Fechamento do Caixa',
                    message:'Caixa Fechado com sucesso! Saldo final: R$ '+PaymentFlow.formatCurrency(this.totalCashier)+ ' Retirada: '+PaymentFlow.formatCurrency(this.withdrawalValue)+' Referente ao mês: '+this.referenceMonth
                    })
            }
        }else{
            this.ModalCloseCashier = false;
            this.totalCashier = this.ValueCashier;
            // logica da API para fechar o caixa

            notificationModal.show({
                title:'Fechamento do Caixa',
                message:'Caixa Fechado com sucesso! Saldo final: R$ '+PaymentFlow.formatCurrency(this.totalCashier)+ ' Retirada: '+PaymentFlow.formatCurrency(this.withdrawalValue)+' Referente ao mês: '+this.referenceMonth
                })
        }
    }

        

    }
}