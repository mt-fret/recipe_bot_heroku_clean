const selector = document.querySelector('select');
const options = document.getElementsByName('ingredients');
const searchForm = document.getElementById('search');
const zeroValue = document.getElementById('zero_value');

searchForm.addEventListener('input', ()=>{
    zeroValue.classList.remove('hidden');
    selector.value = '';
    if (searchForm.value === ''){
        zeroValue.classList.add('hidden');
        selector.value = 'Vegetables';
        get_set();
    }
    options.forEach(o=>{
        if (o.parentElement.innerText.toLowerCase().includes(searchForm.value.toLowerCase())){
            o.parentElement.parentElement.classList.remove('hidden');
                }
        else {
            o.parentElement.parentElement.classList.add('hidden');
        }
    });
});

function get_set(){
        fetch('/get_set/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'ingredient_type': selector.value
            })
    }).then(
        response => {
            return response.json();
        }
    ).then(
        data => {
            options.forEach(o=>{
                if (data.set.includes(Number(o.value))){
                    o.parentElement.parentElement.classList.remove('hidden');
                }
                else {
                    o.parentElement.parentElement.classList.add('hidden');
                }
            });
        }
    )
}

get_set();



selector.addEventListener('change', ()=>{
    zeroValue.classList.add('hidden');
    searchForm.value = ''
get_set();
});