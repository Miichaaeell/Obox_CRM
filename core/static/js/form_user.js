function formHandler(){

    const containerMain = document.getElementById('containerMain');
    let plansData= []
    try {
        plansData = JSON.parse(containerMain.dataset.plans || "[]");
      } catch (e) {
        console.error("Erro ao fazer parse dos planos:", e);
        plansData = [];
      }
    document.addEventListener("DOMContentLoaded", function() {
      const planSelect = document.getElementById("id_plan");
      const valueInput = document.getElementById("value_plan");
      const valueTotal = document.getElementById('total_value');
      const ValueAfterDescount = document.getElementById('value_after_discount')
      const percentDiscount = document.getElementById('percent_discount')
      const valueDiscount = document.getElementById('discount_value')
      planSelect.addEventListener("change", function() {
        const selectedId = parseInt(this.value);
        const plan = plansData.find(p => p.id === selectedId);
        if (plan) {
          valueInput.value = plan.price;
          valueTotal.value = plan.price;
          ValueAfterDescount.value = plan.price;
          percentDiscount.value = "";
          valueDiscount.value = "";
           
        } else {
          valueInput.value = '';
          valueTotal.value = '';
          ValueAfterDescount.value =  "";
        }
    });
      percentDiscount.addEventListener('change', function(){
        const discount = valueInput.value - (valueTotal.value * percentDiscount.value / 100) 
        ValueAfterDescount.value = discount
        valueTotal.value = discount
      })
      valueDiscount.addEventListener('change', function(){
        const discount = valueInput.value - valueDiscount.value
        ValueAfterDescount.value = discount
        valueTotal.value = discount
      })
  // inicializa no load
    if (planSelect.value) {
      const plan = plansData.find(p => p.id === parseInt(planSelect.value));
      if (plan) {
        valueInput.value = plan.price;
      }
    }
  });
}