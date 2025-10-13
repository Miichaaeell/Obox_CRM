function actions(){
    return{
        openModalDelete: false,
        openModalUpdate: false,
        openActiveModal:false,
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
        
        openActive(student){
            this.url = student.urlUpdate || this.url;
            this.openActiveModal = true;

            this.$nextTick(() => {
                const modalContainer = document.getElementById('containerMain');
                if (!modalContainer) {
                    return;
                }

                const alpineData = window.Alpine && typeof window.Alpine.$data === 'function'
                    ? window.Alpine.$data(modalContainer)
                    : null;

                if (alpineData && typeof alpineData.resetPaymentFlow === 'function') {
                    alpineData.resetPaymentFlow();
                    if (typeof alpineData.applyDiscountEnabled === 'function') {
                        alpineData.applyDiscountEnabled(true);
                    }
                    alpineData.registerModal = false;
                    alpineData.isSubmitting = false;
                    alpineData.alert = false;
                    alpineData.validationMessage = '';
                    alpineData.setPaymentData({ payerName: student.name || '' });
                    if (typeof alpineData.updateValidation === 'function') {
                        alpineData.updateValidation();
                    }
                }

                const fieldMap = [
                    { selector: 'input[name="name"]', key: 'name' },
                    { selector: 'input[name="cpf_cnpj"]', key: 'cpf_cnpj' },
                    { selector: 'input[name="date_of_birth"]', key: 'date_of_birth' },
                    { selector: 'input[name="phone_number"]', key: 'phone_number' },
                ];

                fieldMap.forEach(({ selector, key }) => {
                    const input = modalContainer.querySelector(selector);
                    if (input && Object.prototype.hasOwnProperty.call(student, key)) {
                        input.value = student[key] || '';
                    }
                });

                const planSelect = modalContainer.querySelector('select[name="plan"]');
                if (planSelect) {
                    if (student.planId) {
                        planSelect.value = student.planId;
                    }
                    planSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
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
