document.addEventListener('DOMContentLoaded', function () {
    const burgerForm = document.getElementById('burger-form');
    if (!burgerForm) {
        console.error("Burger form not found!");
        return;
    }

    const selectedIngredientsContainer = document.getElementById('selected-ingredients-container');
    const availableIngredientsList = document.getElementById('available-ingredients-list');
    const hiddenFieldsContainer = document.getElementById('hidden-ingredient-fields');
    const noIngredientsPlaceholderOriginal = document.getElementById('no-ingredients-placeholder');

    let selectedIngredients = []; // Array to store {id, name} of selected ingredients

    // Initialize with pre-selected ingredients if 'initialSelectedIngredients' is available (for edit mode)
    if (typeof initialSelectedIngredients !== 'undefined' && Array.isArray(initialSelectedIngredients)) {
        selectedIngredients = [...initialSelectedIngredients]; // Use a copy
    }

    function updateSelectedIngredientsDisplay() {
        if (!selectedIngredientsContainer) return;
        selectedIngredientsContainer.innerHTML = ''; // Clear current display

        if (selectedIngredients.length === 0) {
            if (noIngredientsPlaceholderOriginal) {
                const placeholderClone = noIngredientsPlaceholderOriginal.cloneNode(true);
                selectedIngredientsContainer.appendChild(placeholderClone);
                placeholderClone.style.display = 'block'; // Ensure it's visible
            }
        } else {
            if (noIngredientsPlaceholderOriginal) {
                 // We don't need to hide the original, just don't append it if there are items.
            }
            selectedIngredients.forEach((ingredient, index) => {
                const item = document.createElement('span');
                item.classList.add('selected-ingredient-item');
                item.textContent = ingredient.name + ' '; // Add a space for the 'x'

                const removeBtn = document.createElement('button');
                removeBtn.classList.add('remove-ingredient-btn');
                removeBtn.type = 'button';
                removeBtn.textContent = 'x';
                // removeBtn.dataset.index = index; // Storing index is less robust if array order changes.

                removeBtn.addEventListener('click', function() {
                    // Remove the specific ingredient instance.
                    // This relies on the 'index' from the forEach loop's current state.
                    selectedIngredients.splice(index, 1);
                    updateSelectedIngredientsDisplay(); // Re-render the list
                });

                item.appendChild(removeBtn);
                selectedIngredientsContainer.appendChild(item);
            });
        }
    }

    // Add event listeners to "Add Ingredient" buttons
    if (availableIngredientsList) {
        availableIngredientsList.querySelectorAll('.add-ingredient-btn').forEach(button => {
            button.addEventListener('click', function() {
                const id = this.dataset.ingredientId;
                const name = this.dataset.ingredientName;
                selectedIngredients.push({ id: id, name: name });
                updateSelectedIngredientsDisplay();
            });
        });
    }

    // Before submitting the form, populate hidden input fields for ingredient_ids
    burgerForm.addEventListener('submit', function() {
        if (!hiddenFieldsContainer) return;
        hiddenFieldsContainer.innerHTML = ''; // Clear any old hidden fields
        selectedIngredients.forEach(ingredient => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'ingredient_ids'; // Must match the name expected by the backend
            input.value = ingredient.id;
            hiddenFieldsContainer.appendChild(input);
        });
        // Allow default form submission to proceed
    });

    // Initial call to set up the display based on selectedIngredients array
    updateSelectedIngredientsDisplay();
});