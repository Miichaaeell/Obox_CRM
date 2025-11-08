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
            
        }
    }
}