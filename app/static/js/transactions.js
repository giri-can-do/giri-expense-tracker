document.addEventListener("DOMContentLoaded", () => {
    const filterForm = document.getElementById(
        "transactionFilterForm"
    );

    const startDateInput = document.getElementById(
        "startDate"
    );

    const endDateInput = document.getElementById(
        "endDate"
    );

    const quickDateButtons = document.querySelectorAll(
        ".quick-date-btn"
    );

    if (
        !filterForm ||
        !startDateInput ||
        !endDateInput ||
        quickDateButtons.length === 0
    ) {
        return;
    }

    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(
            date.getMonth() + 1
        ).padStart(2, "0");

        const day = String(
            date.getDate()
        ).padStart(2, "0");

        return `${year}-${month}-${day}`;
    };

    const cloneDate = (date) => {
        return new Date(
            date.getFullYear(),
            date.getMonth(),
            date.getDate()
        );
    };

    const getMonday = (date) => {
        const result = cloneDate(date);
        const day = result.getDay();

        const difference = day === 0
            ? -6
            : 1 - day;

        result.setDate(
            result.getDate() + difference
        );

        return result;
    };

    const getDateRange = (range) => {
        const today = new Date();

        let startDate;
        let endDate;

        switch (range) {
            case "today":
                startDate = cloneDate(today);
                endDate = cloneDate(today);
                break;

            case "yesterday":
                startDate = cloneDate(today);
                startDate.setDate(
                    startDate.getDate() - 1
                );

                endDate = cloneDate(startDate);
                break;

            case "this_week":
                startDate = getMonday(today);
                endDate = cloneDate(today);
                break;

            case "last_week":
                endDate = getMonday(today);
                endDate.setDate(
                    endDate.getDate() - 1
                );

                startDate = cloneDate(endDate);
                startDate.setDate(
                    startDate.getDate() - 6
                );
                break;

            case "this_month":
                startDate = new Date(
                    today.getFullYear(),
                    today.getMonth(),
                    1
                );

                endDate = cloneDate(today);
                break;

            case "last_month":
                startDate = new Date(
                    today.getFullYear(),
                    today.getMonth() - 1,
                    1
                );

                endDate = new Date(
                    today.getFullYear(),
                    today.getMonth(),
                    0
                );
                break;

            case "this_year":
                startDate = new Date(
                    today.getFullYear(),
                    0,
                    1
                );

                endDate = cloneDate(today);
                break;

            case "last_year":
                startDate = new Date(
                    today.getFullYear() - 1,
                    0,
                    1
                );

                endDate = new Date(
                    today.getFullYear() - 1,
                    11,
                    31
                );
                break;

            default:
                return null;
        }

        return {
            startDate: formatDate(startDate),
            endDate: formatDate(endDate),
        };
    };

    const clearActiveButton = () => {
        quickDateButtons.forEach((button) => {
            button.classList.remove("active");
        });
    };

    quickDateButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const range = button.dataset.range;
            const dates = getDateRange(range);

            if (!dates) {
                return;
            }

            startDateInput.value = dates.startDate;
            endDateInput.value = dates.endDate;

            clearActiveButton();
            button.classList.add("active");

            filterForm.submit();
        });
    });

    const handleManualDateChange = () => {
        clearActiveButton();
    };

    startDateInput.addEventListener(
        "change",
        handleManualDateChange
    );

    endDateInput.addEventListener(
        "change",
        handleManualDateChange
    );
});