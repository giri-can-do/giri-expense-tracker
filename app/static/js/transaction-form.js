const typeSelect = document.getElementById("transaction_type");
const categorySelect = document.getElementById("category_id");
const categoryGroup = document.getElementById("categoryGroup");

const liabilitySelect = document.getElementById("liability_id");
const liabilityGroup = document.getElementById("liabilityGroup");

if (typeSelect && categorySelect) {
    const originalCategoryOptions = Array.from(
        categorySelect.querySelectorAll("option[data-type]")
    );

    function updateTransactionFields() {
        const selectedType = typeSelect.value;
        const isDebtPayment = selectedType === "debt_payment";

        categoryGroup.classList.toggle("hidden", isDebtPayment);
        liabilityGroup.classList.toggle("hidden", !isDebtPayment);

        categorySelect.required = !isDebtPayment && Boolean(selectedType);
        liabilitySelect.required = isDebtPayment;

        if (isDebtPayment) {
            categorySelect.value = "";
            categorySelect.disabled = true;
            liabilitySelect.disabled = false;
            return;
        }

        liabilitySelect.value = "";
        liabilitySelect.disabled = true;
        categorySelect.disabled = !selectedType;

        categorySelect.innerHTML =
            '<option value="">Select category</option>';

        originalCategoryOptions
            .filter((option) => option.dataset.type === selectedType)
            .forEach((option) => {
                categorySelect.appendChild(option.cloneNode(true));
            });
    }

    typeSelect.addEventListener("change", updateTransactionFields);

    updateTransactionFields();
}