function flowCashier() {
  return {
    url:'',

    donwloadRelatorio(id, url){
        fetch(url+'?pk='+id, {
          method:'GET',
          headers:{
            'Content-Type':'application/json',
        }}).then(response => response.json())
        .then(data => {
            notificationModal.show({
              title: data.title,
              message: data.message,
            })
        })
    
        notificationModal.show({
              title: 'Download do Fluxo de Caixa',
              message: 'O download do fluxo de caixa está em construção.',
              })
    },
  };
}