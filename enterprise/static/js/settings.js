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
            await fetch(url, {
                method: 'DELETE',
                headers:headers,
            }).then((response) => {
                if(response.ok){
                location.reload()
            }else{
                return response.json()
            }
            }).then((data) =>{
                alert(data['detail'])
            })
            .catch((error) =>{
                console.log(error.message)
            })

        },

        async ClearForm(){
            this.formData = {}
            this.mode = 'create'
        },

        async EditForm(url, form){
            const response = await fetch(url)
            const data = await response.json()
            this.formData = data
            this.mode = 'update'
            this.url = url
            switch(form){
                case "plan":
                    this.menu = 'create-plan';
                    break
                case "service":
                    this.menu = 'create-service';
                    break
                case 'payment':
                    this.menu = 'create-payment'
                    break
            }
        },

        async GetInfoEnterprise(url){
            const response = await fetch(url)
            const data = await response.json()
            this.formData = data
        },

        async UpdateInfoEnterprise(url){
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value
            const headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf,
            }
            const response = await fetch(url, {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify(this.formData)
            })
            if(!response.ok){
                const res = []
                const retorno = await response.json()

                console.log(retorno)
                alert('Erro ao atualizar a empresa')
            }else{
                alert('Dados Atualizados com Sucesso!')
                window.location.reload()
            }
        },
        async SearchCep(){
            base_url = "https://viacep.com.br/ws/"
            await fetch(base_url+this.formData.cep+'/json/')
            .then((response) =>{
                if(response.ok){
                    return response.json()
                }
                else{
                    console.log(response)
                }
            }).then((data) => {
                this.formData.street = data['logradouro']
                this.formData.neighborhood = data['bairro']
                this.formData.city = data['localidade']
                this.formData.state = data['uf']

            }).catch((error)=>{
                console.log(error.message)
            })


        }
    }
}
