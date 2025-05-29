        // Toggle sidebar on mobile
        document.addEventListener('DOMContentLoaded', function() {
            const navbarToggler = document.querySelector('.navbar-toggler');
            const sidebar = document.querySelector('.sidebar');
            
            if (navbarToggler && sidebar) {
                navbarToggler.addEventListener('click', function() {
                    sidebar.classList.toggle('active');
                });
            }
            
            // Highlight active dropdown items
            const dropdownItems = document.querySelectorAll('.dropdown-item');
            dropdownItems.forEach(item => {
                if (item.classList.contains('active')) {
                    item.closest('.dropdown-menu').previousElementSibling.classList.add('active');
                }
            });
        });






        // Enable Bootstrap tooltips
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        });











        // #############################################################################
        // Document ready handler - runs when page is fully loaded
// $(document).ready(function() {
    
//     // =============================================
//     // PRODUCT SELECTION AND ITEM MANAGEMENT
//     // =============================================
    
//     // Array to store all items in the current sale
//     const saleItems = [];

//     // Handle product selection from dropdown
//     $('#sale-create-product-search').change(function() {
//         const selectedOption = $(this).find('option:selected');
//         if (selectedOption.val()) {
//             // Extract product details and add to sale
//             addProductToSale(
//                 selectedOption.val(),      // Product ID
//                 selectedOption.text().split(' - ')[0],  // Product name
//                 parseFloat(selectedOption.data('price')),  // Price
//                 parseInt(selectedOption.data('stock'))     // Available stock
//             );
//             $(this).val(''); // Reset dropdown selection
//         }
//     });

//     // Add a product to the sale
//     function addProductToSale(id, name, price, stock) {
//         // Check if product already exists in sale
//         const existingItem = saleItems.find(item => item.id === id);
        
//         if (existingItem) {
//             // If exists, increase quantity if stock allows
//             if (existingItem.quantity < stock) {
//                 existingItem.quantity++;
//                 existingItem.total = existingItem.quantity * existingItem.price;
//                 updateItemInTable(existingItem);
//             } else {
//                 alert('Cannot add more than available stock!');
//             }
//         } else {
//             // If new product, create item object
//             const newItem = {
//                 id: id,
//                 name: name,
//                 price: price,
//                 quantity: 1,
//                 total: price,
//                 stock: stock
//             };
//             saleItems.push(newItem);  // Add to array
//             addItemToTable(newItem);  // Add to HTML table
//         }
//         updateTotals();  // Recalculate all totals
//     }

//     // Add item row to the HTML table
//     function addItemToTable(item) {
//         const row = `
//             <tr data-id="${item.id}">
//                 <td>${item.name}</td>
//                 <td>ETB ${item.price.toFixed(2)}</td>
//                 <td>
//                     <input type="number" class="form-control sale-create-item-quantity" 
//                            value="${item.quantity}" min="1" max="${item.stock}">
//                 </td>
//                 <td class="sale-create-item-total">ETB ${item.total.toFixed(2)}</td>
//                 <td>
//                     <button class="btn btn-danger btn-sm sale-create-remove-item">
//                         <i class="fas fa-trash"></i>
//                     </button>
//                 </td>
//             </tr>
//         `;
//         $('#sale-create-items-table tbody').append(row);
//     }

//     // Update existing item in HTML table
//     function updateItemInTable(item) {
//         const row = $(`#sale-create-items-table tr[data-id="${item.id}"]`);
//         row.find('.sale-create-item-quantity').val(item.quantity);
//         row.find('.sale-create-item-total').text('ETB ' + item.total.toFixed(2));
//     }

//     // =============================================
//     // EVENT HANDLERS FOR ITEM MANAGEMENT
//     // =============================================

//     // Handle quantity changes for items
//     $('#sale-create-items-table').on('change', '.sale-create-item-quantity', function() {
//         const row = $(this).closest('tr');
//         const id = row.data('id');
//         const newQuantity = parseInt($(this).val());
//         const stock = parseInt($(this).attr('max'));
        
//         // Validate against available stock
//         if (newQuantity > stock) {
//             alert('Cannot exceed available stock!');
//             $(this).val(stock);
//             return;
//         }
        
//         // Update item in array and table
//         const item = saleItems.find(item => item.id === id);
//         if (item) {
//             item.quantity = newQuantity;
//             item.total = item.price * newQuantity;
//             row.find('.sale-create-item-total').text('ETB ' + item.total.toFixed(2));
//             updateTotals();
//         }
//     });

//     // Handle item removal
//     $('#sale-create-items-table').on('click', '.sale-create-remove-item', function() {
//         const row = $(this).closest('tr');
//         const id = row.data('id');
        
//         // Remove from array
//         const index = saleItems.findIndex(item => item.id === id);
//         if (index !== -1) {
//             saleItems.splice(index, 1);
//         }
        
//         // Remove from table
//         row.remove();
//         updateTotals();
//     });

//     // =============================================
//     // CALCULATION FUNCTIONS
//     // =============================================

//     // Calculate and update all totals
//     function updateTotals() {
//         // Calculate subtotal (sum of all item totals)
//         const subTotal = saleItems.reduce((sum, item) => sum + item.total, 0);
        
//         // Get tax percentage and amount paid (default to 0 if empty)
//         const taxPercentage = parseFloat($('input[name="tax_percentage"]').val()) || 0;
//         const amountPaid = parseFloat($('input[name="amount_paid"]').val()) || 0;

//         // Calculate tax and grand total
//         const taxAmount = subTotal * (taxPercentage / 100);
//         const grandTotal = subTotal + taxAmount;
//         const change = amountPaid - grandTotal;

//         // Update visible fields
//         $('#sale-create-subtotal-display').text('ETB ' + subTotal.toFixed(2));
//         $('#sale-create-tax-amount').val(taxAmount.toFixed(2));
//         $('#sale-create-grand-total').val(grandTotal.toFixed(2));
//         $('#sale-create-amount-change').val(change.toFixed(2));
        
//         // Update hidden form field for subtotal
//         $('#sale-create-subtotal').val(subTotal.toFixed(2));
        
//         // Visual feedback for negative change
//         if (change < 0) {
//             $('#sale-create-amount-change').addClass('text-danger');
//         } else {
//             $('#sale-create-amount-change').removeClass('text-danger');
//         }
//     }

//     // Update totals when tax or payment values change
//     $('input[name="tax_percentage"], input[name="amount_paid"]').on('input', updateTotals);

//     // =============================================
//     // FORM SUBMISSION HANDLING
//     // =============================================

//     // Handle form submission
//     $('#sale-create-form').on('submit', function(e) {
//         e.preventDefault();  // Prevent default form submission
        
//         // Validate at least one product exists
//         if (saleItems.length === 0) {
//             alert('Please add at least one product!');
//             return;
//         }

//         // Validate subtotal is positive
//         const subTotal = parseFloat($('#sale-create-subtotal').val());
//         if (isNaN(subTotal) || subTotal <= 0) {
//             alert('Please add at least one product with valid price!');
//             return;
//         }

//         // Get CSRF token for security
//         const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    
//         // Prepare form data for AJAX submission
//         const formData = new FormData();
        
//         // Add form fields
//         formData.append('customer', $('select[name="customer"]').val());
//         formData.append('sub_total', $('#sale-create-subtotal').val());
//         formData.append('tax_percentage', $('input[name="tax_percentage"]').val());
//         formData.append('amount_paid', $('input[name="amount_paid"]').val());
        
//         // Add all sale items
//         saleItems.forEach((item, index) => {
//             formData.append(`items[${index}][id]`, item.id);
//             formData.append(`items[${index}][price]`, item.price);
//             formData.append(`items[${index}][quantity]`, item.quantity);
//         });
        
//         // Disable submit button during processing
//         const submitBtn = $(this).find('button[type="submit"]');
//         submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Processing...');

//         // Submit via AJAX
//         $.ajax({
//             url: $(this).attr('action'),
//             type: 'POST',
//             data: formData,
//             processData: false,  // Required for FormData
//             contentType: false,  // Required for FormData
//             headers: {
//                 'X-CSRFToken': csrftoken,
//                 'X-Requested-With': 'XMLHttpRequest'
//             },
//             success: function(response) {
//                 // On success, redirect to sales list
//                 if (response.success || response.redirect) {
//                     window.location.href = response.redirect || '{% url "transactions:sale-list" %}';
//                 } else {
//                     // Show error if response indicates failure
//                     alert(response.error || 'Error processing sale');
//                     submitBtn.prop('disabled', false).html('Complete Sale');
//                 }
//             },
//             error: function(xhr) {
//                 // Handle AJAX errors
//                 let errorMsg = 'Sale processing failed';
//                 if (xhr.responseJSON && xhr.responseJSON.error) {
//                     errorMsg = xhr.responseJSON.error;
//                 } else if (xhr.statusText) {
//                     errorMsg += ': ' + xhr.statusText;
//                 }
//                 alert(errorMsg);
//                 submitBtn.prop('disabled', false).html('Complete Sale');
//             }
//         });
//     });
// });

// #############################################################################











