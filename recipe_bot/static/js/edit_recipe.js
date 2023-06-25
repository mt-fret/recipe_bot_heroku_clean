const inputForm = document.querySelector('.input_form');
const messageInput = document.querySelector('.input_input');
const recipeError = document.getElementById('recipe_error');
const addNewRecipe = document.getElementById('create_new_recipe');
const updateRecipe = document.getElementById('update_recipe');


const recipeName = document.getElementById('recipe_name');
const recipeDescription = document.getElementById('recipe_description');
const recipeIngredients = document.getElementById('recipe_ingredients');
const recipeSteps = document.getElementById('recipe_steps');
const recipePrepTime = document.getElementById('recipe_prep_time');
const recipeCookTime = document.getElementById('recipe_cook_time');
const recipeCuisine = document.getElementById('recipe_cuisine');
const recipeServes = document.getElementById('recipe_serves');

updateRecipe.addEventListener('submit', (e)=>{
    if (recipeName.innerText === '-'){
        e.preventDefault();
    }
})


addNewRecipe.addEventListener('submit', (e)=>{
    if (recipeName.innerText === '-'){
        e.preventDefault();
    }
})

inputForm.addEventListener('submit', e=>{
    e.preventDefault();
    const message = messageInput.value.trim();
    if (message.length === 0){
        return;
    }
    loading_animation()
    messageInput.value = '';

    fetch('/create_recipe/', {
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