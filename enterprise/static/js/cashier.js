function CashierHandler(){
    return {
        ModalCloseCashier:false,
        withdrawal:false,
        withdrawalValue:0.00,
        referenceMonth:null,
        totalCashier:0.00,
    
    startclosecashier(){
        this.referenceMonth = new Date().toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
        this.ModalCloseCashier = true;
    
    },
    flowclosecashier(){
        this.ModalCloseCashier = false;
        
        notificationModal.show({
            title:'Fechamento do Caixa',
            message:'Caixa Fechado com sucesso!'
        })
    }

    }
}