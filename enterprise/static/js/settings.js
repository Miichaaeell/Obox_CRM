function SettingsHandler(){
    return{
        menu:'plans',
        formData:{},

        async SubmitForm(){
            console.log(this.formData)
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
                data = await response.json()
                console.log(data)
                setTimeout(function(){location.reload()}, 5000)
            }
        }
    }
}