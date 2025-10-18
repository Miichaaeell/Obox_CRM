function flowCashier() {
  return {
    url:'',

    donwloadRelatorio(id, url){
      notificationModal.show({
        title: 'Baixando relatório',
        message: 'Por favor, aguarde enquanto o relatório está sendo preparado para download...',
      })
        fetch(url+'?pk='+id, {
          method:'GET',
          headers: {
            'Content_Type': 'application/json'
          }
          }).then(async response => {
          const contentType = response.headers.get('Content-Type') || '';
          if (!response.ok || (!contentType.includes('spreadsheet') && !contentType.includes('excel'))) {
            const data = await response.json();
            throw new Error(data.message || 'Erro ao gerar o relatório.');
          }
          // 🟢 Extrai o nome do arquivo do cabeçalho
          const disposition = response.headers.get('Content-Disposition');
          let filename = 'relatorio.xlsx';
          if (disposition && disposition.includes('filename=')) {
            filename = disposition
              .split('filename=')[1]
              .split(';')[0]
              .replace(/["']/g, '')
              .trim();
          }
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = filename
          document.body.appendChild(link)
          link.click()
          link.remove()
          window.URL.revokeObjectURL(url)
        })
        .catch(error => {
          console.error('There was a problem with the fetch operation:', error);
          notificationModal.show({
              title: 'Erro ao baixar o relatório',
              message: error.message,
              })
        }).finally(()=> notificationModal.close())
    
        
    },
  };
}