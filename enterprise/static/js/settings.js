function SettingsHandler(){
    return{
        menu:'info',
        formData:{},
        mode:'create',
        url:'',

        async SubmitForm(url){
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf,
            };
            const fetch_url = this.mode == 'create' ? url : this.url
            const method = this.mode == 'create' ? 'POST' : 'PUT'
            const response = await fetch(fetch_url, {
                method: method,
                headers: headers,
                body: JSON.stringify(this.formData)
                })
                if(!response.ok){
                    console.log('Erro ao realizar o fetch para a API')
                }else{
                    location.reload()
                }
        },

        async DeleteForm(url){
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
        },

        async EditForm(url, form){
            const response = await fetch(url)
            const data = await response.json()
            this.formData = data
            this.mode = 'update'
            this.url = url
            this.menu = form == 'plan' ? 'create-plan' : 'create-service'
        }
    }
}