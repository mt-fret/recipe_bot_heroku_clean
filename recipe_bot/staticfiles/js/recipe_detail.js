function toggle(check_all){
    const checkIngredients = document.getElementsByName('missing_ingredient');
    for (let i = 0; i < checkIngredients.length; i++){
        if (checkIngredients[i] != check_all){
            checkIngredients[i].checked = check_all.checked;
        }
    }
}