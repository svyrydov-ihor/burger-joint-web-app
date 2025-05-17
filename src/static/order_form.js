document.addEventListener('DOMContentLoaded', function () {
    const orderForm = document.getElementById('order-form');
    if (!orderForm) return;

    const selectedItemsContainer = document.getElementById('selected-order-items-container');
    const noItemsPlaceholderOriginal = document.getElementById('no-items-placeholder');
    const hiddenItemFieldsContainer = document.getElementById('hidden-order-item-fields');

    const selectBurgerElement = document.getElementById('select_burger');
    const itemQuantityElement = document.getElementById('item_quantity');
    const addItemBtn = document.getElementById('add-order-item-btn');

    let currentOrderItems = []; // Array of { burger_id, burger_name, quantity, price }

    // Initialize with pre-selected items if 'initialOrderItems' is available (for edit mode)
    if (typeof initialOrderItems !== 'undefined' && Array.isArray(initialOrderItems)) {
        currentOrderItems = [...initialOrderItems]; // { burger_id, burger_name, quantity, price }
    }

    // Map available burger data for easy lookup
    const burgerDataMap = new Map();
    if (typeof availableBurgers !== 'undefined' && Array.isArray(availableBurgers)) {
        availableBurgers.forEach(b => burgerDataMap.set(b.id.toString(), { name: b.name, price: b.price }));
    }

    function renderOrderItems() {
        if (!selectedItemsContainer) return;
        selectedItemsContainer.innerHTML = ''; // Clear current display

        if (currentOrderItems.length === 0) {
            if (noItemsPlaceholderOriginal) {
                const placeholderClone = noItemsPlaceholderOriginal.cloneNode(true);
                selectedItemsContainer.appendChild(placeholderClone);
                placeholderClone.style.display = 'block';
            }
        } else {
            currentOrderItems.forEach((item, index) => {
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('selected-order-item-display'); // Add a class for styling
                itemDiv.style.padding = '5px';
                itemDiv.style.borderBottom = '1px solid #eee';

                const burgerInfo = burgerDataMap.get(item.burger_id.toString());
                const itemName = burgerInfo ? burgerInfo.name : (item.burger_name || 'Unknown Burger');
                const itemPrice = burgerInfo ? burgerInfo.price : (item.price || 0);
                const subtotal = (item.quantity * itemPrice).toFixed(2);

                itemDiv.innerHTML = `
                    <span>${itemName} (ID: ${item.burger_id})</span><br>
                    <span>Qty: 
                        <input type="number" value="${item.quantity}" min="1" class="item-quantity-input" data-index="${index}" style="width: 60px;">
                         x $${itemPrice.toFixed(2)} = $${subtotal}
                    </span>
                    <button type="button" class="remove-order-item-btn" data-index="${index}" style="margin-left: 10px; color: red; background: none; border: none; cursor: pointer;">&times;</button>
                `;
                selectedItemsContainer.appendChild(itemDiv);
            });

            // Add event listeners for quantity inputs and remove buttons
            selectedItemsContainer.querySelectorAll('.item-quantity-input').forEach(input => {
                input.addEventListener('change', function() {
                    const index = parseInt(this.dataset.index);
                    const newQuantity = parseInt(this.value);
                    if (newQuantity >= 1 && index < currentOrderItems.length) {
                        currentOrderItems[index].quantity = newQuantity;
                        renderOrderItems(); // Re-render to update subtotal and reflect change
                    } else { // Reset to old value or handle error
                        this.value = currentOrderItems[index].quantity;
                    }
                });
            });

            selectedItemsContainer.querySelectorAll('.remove-order-item-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const index = parseInt(this.dataset.index);
                    currentOrderItems.splice(index, 1);
                    renderOrderItems();
                });
            });
        }
    }

    if (addItemBtn && selectBurgerElement && itemQuantityElement) {
        addItemBtn.addEventListener('click', function() {
            const burgerId = selectBurgerElement.value;
            const quantity = parseInt(itemQuantityElement.value);
            const selectedOption = selectBurgerElement.options[selectBurgerElement.selectedIndex];

            if (!burgerId || quantity < 1) {
                alert("Please select a burger and enter a valid quantity.");
                return;
            }

            const burgerInfo = burgerDataMap.get(burgerId.toString());
            if (!burgerInfo) {
                alert("Selected burger data not found.");
                return;
            }

            // Check if item already exists, if so, update quantity (optional, or allow duplicates)
            const existingItemIndex = currentOrderItems.findIndex(item => item.burger_id === burgerId);
            if (existingItemIndex > -1) {
                 // Option 1: Update quantity of existing item
                currentOrderItems[existingItemIndex].quantity += quantity;
                 // Option 2: Or add as a new line (current implementation adds new line by default)
                 // currentOrderItems.push({ burger_id: burgerId, burger_name: burgerInfo.name, quantity: quantity, price: burgerInfo.price });
            } else {
                 currentOrderItems.push({ burger_id: burgerId, burger_name: burgerInfo.name, quantity: quantity, price: burgerInfo.price });
            }

            renderOrderItems();
            // Reset add item fields
            selectBurgerElement.value = "";
            itemQuantityElement.value = "1";
        });
    }

    orderForm.addEventListener('submit', function() {
        if (!hiddenItemFieldsContainer) return;
        hiddenItemFieldsContainer.innerHTML = ''; // Clear old fields

        currentOrderItems.forEach(item => {
            const burgerIdInput = document.createElement('input');
            burgerIdInput.type = 'hidden';
            burgerIdInput.name = 'item_burger_ids'; // Parallel arrays
            burgerIdInput.value = item.burger_id;
            hiddenItemFieldsContainer.appendChild(burgerIdInput);

            const quantityInput = document.createElement('input');
            quantityInput.type = 'hidden';
            quantityInput.name = 'item_quantities'; // Parallel arrays
            quantityInput.value = item.quantity;
            hiddenItemFieldsContainer.appendChild(quantityInput);
        });
    });

    // Initial render of items (e.g., for edit mode)
    renderOrderItems();
});