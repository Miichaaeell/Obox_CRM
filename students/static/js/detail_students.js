function actions(){
    return{
        openModalDelete: false,
        openModalUpdate: false,
        studentData:{},
        url:'',


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
        },

        openUpdate(student){
            this.url = student.urlUpdate
            this.studentData={
                id:student.id,
                name: student.name,
                cpf_cnpj: student.cpf_cnpj,
                date_of_birth: student.date_of_birth,
                phone_number: student.phone_number,
            };
            this.openModalUpdate = true
        },

        async changeStudent(){
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
            header = {
                'Content-Type' : 'application/json',
                "X-CSRFToken": csrftoken,
            }
            const response = await fetch(this.url, {
                method: 'PATCH',
                headers: header,
                body: JSON.stringify(this.studentData)
            });

            if (response.ok){
                this.openModalUpdate = false,
                window.location.reload()
            } else{
                data = response.json()
                console.log(data)
                alert('erro ao editar o aluno')                
            }
        },
    }
}