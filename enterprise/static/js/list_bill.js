function modalHandler(){
  return{
    showModal: false,
    showStatus : false,
    showDelete: false,
    applydiscount:false,
    formData: {},
    mode: '',
    selectedID: null,

    modalcreate(){
      this.mode = 'create'
      this.formData={
        'description': '',
        'value': '',
        'due_date': '',
        'appellant':false,
        'apply_discount':false,
        'payment_method': null,
        'status': null,
      },
      this.showModal = true
    },

    async modalupdate(id){
      const res = await fetch(`/bill/api/v1/${id}`);
      const data = await res.json();
      this.formData = data;
      this.mode = 'update';
      this.selectedID = id;
      this.showModal = true;
    },

    async modalstatus(id){
      const res = await fetch(`/bill/api/v1/${id}`);
      const data = await res.json();
      this.formData = data;
      this.mode = 'update';
      this.selectedID = id;
      this.showStatus = true;
    },
    async modaldelete(id){
      const res = await fetch(`/bill/api/v1/${id}`);
      const data = await res.json();
      this.formData = data;
      this.mode = 'delete';
      this.selectedID = id;
      this.showDelete = true;

    },

    modalclose(){
      this.showModal = false,
      this.showStatus = false,
      this.showDelete= false
    },

    recalcTotal() {
      let total = Number(this.formData.value) || 0;

      if (this.formData.apply_discount) {
        if (this.formData.percent_discount) {
          total -= total * (this.formData.percent_discount / 100);
        }
        if (this.formData.value_discount) {
          total -= Number(this.formData.value_discount);
        }
        if (this.formData.percent_fine) {
          total += (this.formData.value * this.formData.percent_fine / 100);
        }
        if (this.formData.value_fine) {
          total += Number(this.formData.value_fine);
        }
      }

      this.formData.total_value = total.toFixed(2);
    },

    async submitForm(){
      const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value
      const header = {
        'Content-Type': 'application/json',
        "X-CSRFToken": csrftoken
      }
      this.formData.total_value = document.getElementById('total_value').value
       if (this.mode === 'create') {
        console.log(this.formData)
                await fetch('/bill/api/v1/', {
                    method: 'POST',
                    headers: header,
                    body: JSON.stringify(this.formData)
                }).then(response => response.json()).then(data => {
                  console.log(data)
                })
        } else if (this.mode === 'delete') {
                await fetch(`/bill/api/v1/${this.selectedID}/`, {
                    method: 'DELETE',
                    headers: header,
                })
        } else {
                await fetch(`/bill/api/v1/${this.selectedID}/`, {
                    method: 'PUT',
                    headers: header,
                    body: JSON.stringify(this.formData)
                });
            }
        this.open = false;
        window.location.reload();
    }
  }
}
