function actions(){
    return{
        openModalDelete: false,


        async deleteStudent(id, urlDelete, urlRedirect){
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
            header = {
                'Content-Type': 'application/json',
                "X-CSRFToken": csrftoken
            }
            await fetch(urlDelete,{
                method: 'DELETE',
                headers: header
            })
            window.location.href = urlRedirect;
        }

    }
}