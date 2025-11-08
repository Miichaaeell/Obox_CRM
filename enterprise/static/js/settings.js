function SettingsHandler(){
    return{
        menu:'plans',
        formData:{},
        mode:'create',
        url:'',

        async SubmitForm(){
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf,
            };
            const fetch_url = this.mode == 'create' ? document.getElementById('create_plan').dataset.url : this.url
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
        },

        async EditPlan(url){
            const response = await fetch(url)
            const data = await response.json()
            this.formData = data
            this.mode = 'update'
            this.url = url
            this.menu = 'create-plan'
        }
    }
}