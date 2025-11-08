function SettingsHandler(){
    return{
        menu:'plans',
        formData:{},

        async SubmitForm(){
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf,
            };
            const url = document.getElementById('create_plan').dataset.url
            const response = await fetch(url, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(this.formData)
            })
            if(!response.ok){
                console.log('Erro ao realizar o fetch para a API')
            }else{
                location.reload()
            }
        },

        async DeletePlan(url){
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf,
            }
            const response = await fetch(url, {
                method: 'DELETE',
                headers:headers,
            })
            if(!response.ok){
                console.log('Erro ao tentar deletar o plano')
            }else{
                location.reload()
            }
        }
    }
}