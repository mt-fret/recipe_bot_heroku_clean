const inputForm = document.querySelector('.input_form');
const messageInput = document.querySelector('.input_input');
const saveRecipe = document.getElementById('save_recipe');
const recipeError = document.getElementById('recipe_error');


const createNewRecipe = document.querySelector('.create_new_recipe');
const pantryIngredients = document.querySelectorAll('.pantry_ingredients');
const recipeName = document.getElementById('recipe_name');
const recipeDescription = document.getElementById('recipe_description');
const recipeIngredients = document.getElementById('recipe_ingredients');
const recipeSteps = document.getElementById('recipe_steps');
const recipePrepTime = document.getElementById('recipe_prep_time');
const recipeCookTime = document.getElementById('recipe_cook_time');
const recipeCuisine = document.getElementById('recipe_cuisine');
const recipeServes = document.getElementById('recipe_serves');

saveRecipe.addEventListener('submit', (e)=>{
    if (recipeName.innerText === '-'){
        e.preventDefault();
        return;
    }
})

createNewRecipe.addEventListener('submit', (e)=>{
    e.preventDefault();

    const newRecipeIngredients = [];
    pantryIngredients.forEach(p=> {
        if (p.checked) {
            newRecipeIngredients.push(Number(p.value));
        }
    });

    if (newRecipeIngredients.length === 0){
        return;
    }

    loading_animation()

    const meatOption = document.getElementsByName('meat_option')[0].value;
    const mealType = document.getElementById('meal_type').value;
    const kitchenType = document.getElementById('kitchen_type').value;
    const time = document.getElementById('time').value;
    const additionalInfo = document.getElementById('additional_info').value;

    fetch('/create_new_recipe/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({
            'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'new_recipe_ingredients': newRecipeIngredients,
            'meat_option': meatOption,
            'meal_type': mealType,
            'kitchen_type': kitchenType,
            'time': time,
            'additional_info': additionalInfo
            })
        })
        .then(response => response.json())
        .then(data => {
            assign_data(data)
            });

    })


inputForm.addEventListener('submit', (e)=> {
    e.preventDefault();
    const message = messageInput.value.trim();

    if (message.length === 0) {
        return;
    } else {

        loading_animation()
        messageInput.value = '';

        fetch('', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: new URLSearchParams({
                'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'user_input': message
            })
        })
            .then(
                response => {
                    return response.json();
                }
            ).then(
            data => {
                assign_data(data)
            });
    }
});

function loading_animation() {
    clear_data()
    const singleLoading = document.querySelectorAll('.single');
    const tripleLoading = document.querySelectorAll('.triple');
    singleLoading.forEach(s=>{
        s.classList.add('loading_single');
    });
    tripleLoading.forEach(t=>{
        t.classList.add('loading');
    });
}

function remove_loading_animation(){
    const singleLoading = document.querySelectorAll('.single');
    const tripleLoading = document.querySelectorAll('.triple');
    recipeIngredients.innerHTML = '';
    recipeSteps.innerHTML = '';
    singleLoading.forEach(s=>{
        s.classList.remove('loading_single');
    });
    tripleLoading.forEach(t=>{
        t.classList.remove('loading');
    });
}

function clear_data(){
    recipeName.innerText = '';
    recipeDescription.innerText = '';
    recipeCuisine.innerText = '';
    recipePrepTime.innerText = '';
    recipeCookTime.innerText = '';
    recipeServes.innerText = '';
    recipeIngredients.innerHTML = '<p class="triple"></p>';
    recipeSteps.innerHTML = '<p class="triple"></p>';
}

function assign_data(data){
    remove_loading_animation()
    const recipe = data;

    if (getParam(recipe.error)){
        recipeError.classList.remove('hidden');
        recipeError.innerText = recipe.error;
    } else {
        recipeError.classList.add('hidden');
    }

    recipeName.innerText = recipe.name;
    recipeDescription.innerText = recipe.description;
    recipe.ingredients.forEach(ingredient => {
        const ingredientItem = document.createElement('li');
        ingredientItem.innerText = ingredient;
        recipeIngredients.appendChild(ingredientItem);
        })
    recipe.steps.forEach(step => {
        const stepItem = document.createElement('li');
        stepItem.innerText = step;
        recipeSteps.appendChild(stepItem);
        })
    recipePrepTime.innerText = recipe.prep_time;
    recipeCookTime.innerText = recipe.cook_time;
    recipeCuisine.innerText = recipe.cuisine;
    recipeServes.innerText = recipe.serves;
}

function getParam(param){
    if (param !== undefined){
        return param;
    }
}