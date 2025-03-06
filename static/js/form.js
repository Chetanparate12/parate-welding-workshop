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
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const itemsContainer = document.getElementById('items');
    const addItemButton = document.getElementById('addItem');
    const billForm = document.getElementById('billForm');
    
    // Initialize
    calculateItemTotals();
    updateTotals();
    
    // Add item button
    if (addItemButton) {
        addItemButton.addEventListener('click', function() {
            const itemTemplate = `
                <div class="row item mb-3">
                    <div class="col-md-5">
                        <label class="form-label fw-bold">Description</label>
                        <input type="text" class="form-control description" name="descriptions[]" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label fw-bold">Quantity</label>
                        <input type="number" class="form-control quantity" name="quantities[]" value="1" min="1" step="1" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label fw-bold">Price</label>
                        <input type="number" class="form-control price" name="prices[]" value="0" min="0" step="0.01" required>
                    </div>
                    <div class="col-md-2">
                        <label class="form-label fw-bold">Total</label>
                        <input type="number" class="form-control item-total" readonly>
                    </div>
                    <div class="col-md-1 d-flex align-items-end">
                        <button type="button" class="btn btn-danger remove-item mb-2">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            
            itemsContainer.insertAdjacentHTML('beforeend', itemTemplate);
            
            // Make all remove buttons visible
            document.querySelectorAll('.remove-item').forEach(button => {
                button.style.display = 'block';
            });
            
            // Add event listeners to the new item
            addItemEventListeners(itemsContainer.lastElementChild);
            
            // Add focus to the new item's description field
            const newItem = itemsContainer.lastElementChild;
            const descriptionInput = newItem.querySelector('.description');
            if (descriptionInput) {
                descriptionInput.focus();
            }
            
            // Animate the new row
            newItem.style.opacity = '0';
            newItem.style.transform = 'translateY(20px)';
            newItem.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            // Trigger reflow
            newItem.offsetHeight;
            
            // Apply animation
            newItem.style.opacity = '1';
            newItem.style.transform = 'translateY(0)';
        });
    }
    
    // Add event listeners to existing items
    document.querySelectorAll('.item').forEach(item => {
        addItemEventListeners(item);
    });
    
    // Form submit validation
    if (billForm) {
        billForm.addEventListener('submit', function(event) {
            const amountPaid = parseFloat(document.getElementById('amount_paid').value) || 0;
            const total = parseFloat(document.getElementById('total').value) || 0;
            
            if (amountPaid > total) {
                event.preventDefault();
                alert('Amount paid cannot be greater than the total amount.');
                return false;
            }
            
            // Add subtle loading animation
            const submitButton = billForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Generating...';
            }
            
            return true;
        });
    }
    
    // Event listeners for date input
    const dateInput = document.getElementById('date');
    if (dateInput && !dateInput.value) {
        // Set default date to today
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        dateInput.value = `${yyyy}-${mm}-${dd}`;
    }
    
    // Client name autocomplete
    const clientNameInput = document.getElementById('client_name');
    if (clientNameInput) {
        clientNameInput.addEventListener('input', function() {
            // Here you could implement autocomplete based on previous clients
            // For now, just capitalize the first letter of each word
            let words = this.value.split(' ');
            for (let i = 0; i < words.length; i++) {
                if (words[i].length > 0) {
                    words[i] = words[i][0].toUpperCase() + words[i].substring(1);
                }
            }
            this.value = words.join(' ');
        });
    }
    
    // Helper functions
    function addItemEventListeners(item) {
        const quantityInput = item.querySelector('.quantity');
        const priceInput = item.querySelector('.price');
        const removeButton = item.querySelector('.remove-item');
        
        quantityInput.addEventListener('input', function() {
            calculateItemTotals();
            updateTotals();
        });
        
        priceInput.addEventListener('input', function() {
            calculateItemTotals();
            updateTotals();
        });
        
        removeButton.addEventListener('click', function() {
            // Animate removal
            item.style.opacity = '0';
            item.style.transform = 'translateX(20px)';
            item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            setTimeout(() => {
                item.remove();
                calculateItemTotals();
                updateTotals();
                
                // Hide remove button if only one item remains
                const items = document.querySelectorAll('.item');
                if (items.length === 1) {
                    items[0].querySelector('.remove-item').style.display = 'none';
                }
            }, 300);
        });
    }
    
    function calculateItemTotals() {
        document.querySelectorAll('.item').forEach(item => {
            const quantity = parseFloat(item.querySelector('.quantity').value) || 0;
            const price = parseFloat(item.querySelector('.price').value) || 0;
            const total = quantity * price;
            item.querySelector('.item-total').value = total.toFixed(2);
        });
    }
    
    function updateTotals() {
        let subtotal = 0;
        document.querySelectorAll('.item-total').forEach(itemTotal => {
            subtotal += parseFloat(itemTotal.value) || 0;
        });
        
        const tax = subtotal * 0.18;
        const total = subtotal + tax;
        
        // Update with animation
        animateValue('subtotal', parseFloat(document.getElementById('subtotal').value) || 0, subtotal);
        animateValue('tax', parseFloat(document.getElementById('tax').value) || 0, tax);
        animateValue('total', parseFloat(document.getElementById('total').value) || 0, total);
    }
    
    function animateValue(elementId, start, end) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const duration = 500;
        const startTime = new Date().getTime();
        
        const timer = setInterval(function() {
            const time = new Date().getTime() - startTime;
            const value = easeOutCubic(time, start, end - start, duration);
            
            element.value = value.toFixed(2);
            
            if (time >= duration) {
                clearInterval(timer);
                element.value = end.toFixed(2);
            }
        }, 16);
    }
    
    // Easing function
    function easeOutCubic(t, b, c, d) {
        t /= d;
        t--;
        return c * (t * t * t + 1) + b;
    }
});
