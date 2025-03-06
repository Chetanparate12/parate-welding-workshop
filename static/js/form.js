document.addEventListener('DOMContentLoaded', function() {
    const itemsList = document.getElementById('itemsList');
    const addItemBtn = document.getElementById('addItem');

    function createItemRow() {
        const div = document.createElement('div');
        div.className = 'row mb-3 item-row';
        div.innerHTML = `
            <div class="col-md-3">
                <input type="text" class="form-control" name="item_name[]" placeholder="Item Name" required>
            </div>
            <div class="col-md-2">
                <select class="form-control" name="unit[]" required>
                    <option value="quantity">Quantity</option>
                    <option value="kilogram">Kilogram</option>
                </select>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" name="quantity[]" placeholder="Amount" step="0.01" required>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" name="price[]" placeholder="Price" step="0.01" required>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" name="amount[]" placeholder="Amount" readonly>
            </div>
            <div class="col-md-1">
                <button type="button" class="btn btn-danger btn-sm remove-item">Remove</button>
            </div>
        `;

        const removeBtn = div.querySelector('.remove-item');
        removeBtn.addEventListener('click', function() {
            div.remove();
            calculateTotals();
        });

        const quantityInput = div.querySelector('input[name="quantity[]"]');
        const priceInput = div.querySelector('input[name="price[]"]');
        const amountInput = div.querySelector('input[name="amount[]"]');
        const unitSelect = div.querySelector('select[name="unit[]"]');

        function updateQuantityPlaceholder() {
            const unit = unitSelect.value;
            quantityInput.placeholder = unit === 'quantity' ? 'Quantity' : 'Weight (kg)';
        }

        function calculateAmount() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            amountInput.value = (quantity * price).toFixed(2);
            calculateTotals();
        }

        unitSelect.addEventListener('change', updateQuantityPlaceholder);
        quantityInput.addEventListener('input', calculateAmount);
        priceInput.addEventListener('input', calculateAmount);

        updateQuantityPlaceholder();
        return div;
    }

    function calculateTotals() {
        const amounts = Array.from(document.getElementsByName('amount[]'))
            .map(input => parseFloat(input.value) || 0);

        const subtotal = amounts.reduce((sum, amount) => sum + amount, 0);
        document.getElementById('subtotal').value = subtotal.toFixed(2);
        document.getElementById('total').value = subtotal.toFixed(2);
    }

    addItemBtn.addEventListener('click', function() {
        itemsList.appendChild(createItemRow());
    });

    // Add first item row by default
    itemsList.appendChild(createItemRow());
});