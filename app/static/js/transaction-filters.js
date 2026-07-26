const transactionTypeFilter =
    document.getElementById("transactionType");

const categoryFilter =
    document.getElementById("transactionCategory");

if (transactionTypeFilter && categoryFilter) {
    const originalCategoryOptions = Array.from(
        categoryFilter.querySelectorAll(
            "option[data-category-type]"
        )
    );

    const initialCategoryValue =
        categoryFilter.value;

    function updateCategoryOptions(
        preserveSelectedValue = false
    ) {
        const selectedType =
            transactionTypeFilter.value;

        const selectedCategoryValue =
            preserveSelectedValue
                ? initialCategoryValue
                : "";

        categoryFilter.innerHTML = "";

        const defaultOption =
            document.createElement("option");

        defaultOption.value = "";

        if (selectedType === "income") {
            defaultOption.textContent =
                "All Income Categories";
        } else if (selectedType === "expense") {
            defaultOption.textContent =
                "All Expense Categories";
        } else if (selectedType === "debt_payment") {
            defaultOption.textContent =
                "Not applicable for Debt Payments";
        } else {
            defaultOption.textContent =
                "All Categories";
        }

        categoryFilter.appendChild(defaultOption);

        if (selectedType === "debt_payment") {
            categoryFilter.disabled = true;
            categoryFilter.value = "";
            return;
        }

        categoryFilter.disabled = false;

        originalCategoryOptions.forEach(option => {
            const categoryType =
                option.dataset.categoryType;

            const shouldInclude =
                !selectedType ||
                categoryType === selectedType;

            if (!shouldInclude) {
                return;
            }

            const clonedOption =
                option.cloneNode(true);

            clonedOption.selected =
                clonedOption.value ===
                selectedCategoryValue;

            categoryFilter.appendChild(
                clonedOption
            );
        });

        categoryFilter.value =
            selectedCategoryValue;
    }

    transactionTypeFilter.addEventListener(
        "change",
        () => {
            updateCategoryOptions(false);
        }
    );

    // Preserve a submitted category after page refresh.
    updateCategoryOptions(true);
}