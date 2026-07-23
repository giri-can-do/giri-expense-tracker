const dashboardDataElement =
    document.getElementById("dashboard-data");

if (!dashboardDataElement) {
    console.error("Dashboard chart data element was not found.");
} else if (typeof Chart === "undefined") {
    console.error("Chart.js was not loaded.");
} else {
    const chartData = JSON.parse(
        dashboardDataElement.textContent
    );

    initializeDashboardCharts(chartData);
}

function initializeDashboardCharts(chartData) {
    const sharedOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "#cbd5e1"
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: "#94a3b8"
                },
                grid: {
                    color: "rgba(148, 163, 184, 0.08)"
                }
            },
            y: {
                beginAtZero: true,
                grace: "12%",
                ticks: {
                    color: "#94a3b8",
                    callback(value) {
                        return `¥${Number(value).toLocaleString()}`;
                    }
                },
                grid: {
                    color: "rgba(148, 163, 184, 0.08)"
                }
            }
        }
    };

    const monthlyCanvas = document.getElementById("monthlyTrendChart");

    if (monthlyCanvas && chartData.monthlyTrend) {
        new Chart(monthlyCanvas, {
            type: "bar",
            data: {
                labels: chartData.monthlyTrend.map(item => item.label),
                datasets: [
                    {
                        label: "Income",
                        data: chartData.monthlyTrend.map(item => item.income),
                        backgroundColor: "rgba(34, 197, 94, 0.75)",
                        borderRadius: 6
                    },
                    {
                        label: "Expenses",
                        data: chartData.monthlyTrend.map(item => item.expenses),
                        backgroundColor: "rgba(248, 113, 113, 0.75)",
                        borderRadius: 6
                    }
                ]
            },
            options: sharedOptions
        });
    }

    const expenseCanvas = document.getElementById("expenseCategoryChart");

    if (expenseCanvas && chartData.expenseBreakdown.length > 0) {
        new Chart(expenseCanvas, {
            type: "doughnut",
            data: {
                labels: chartData.expenseBreakdown.map(
                    item => `${item.category_icon || "💸"} ${item.category_name}`
                ),
                datasets: [
                    {
                        data: chartData.expenseBreakdown.map(
                            item => item.amount
                        ),
                        borderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: "#cbd5e1",
                            padding: 12,
                            boxWidth: 12,
                            font: {
                                size: 10
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label(context) {
                                return `${context.label}: ¥${Number(
                                    context.raw
                                ).toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    const savingsCanvas =
        document.getElementById("savingsTrendChart");

    if (savingsCanvas && chartData.monthlyTrend.length > 0) {
        new Chart(savingsCanvas, {
            type: "line",
            data: {
                labels: chartData.monthlyTrend.map(
                    item => item.label
                ),
                datasets: [
                    {
                        label: "Monthly Savings",
                        data: chartData.monthlyTrend.map(
                            item => item.savings
                        ),
                        borderColor: "rgba(34, 197, 94, 1)",
                        backgroundColor: "rgba(34, 197, 94, 0.12)",
                        pointBackgroundColor: context => {
                            return context.raw < 0
                                ? "rgba(248, 113, 113, 1)"
                                : "rgba(34, 197, 94, 1)";
                        },
                        pointBorderColor: context => {
                            return context.raw < 0
                                ? "rgba(248, 113, 113, 1)"
                                : "rgba(34, 197, 94, 1)";
                        },
                        pointRadius: 5,
                        pointHoverRadius: 7,
                        borderWidth: 3,
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                ...sharedOptions,
                plugins: {
                    ...sharedOptions.plugins,
                    tooltip: {
                        callbacks: {
                            label(context) {
                                return `Savings: ¥${Number(
                                    context.raw
                                ).toLocaleString()}`;
                            }
                        }
                    }
                }
            }
        });
    }

    const expenseTrendCanvas =
        document.getElementById("expenseTrendChart");

    const expenseTrendWrapper =
        document.getElementById("expenseTrendWrapper");

    const expenseTrendEmpty =
        document.getElementById("expenseTrendEmpty");

    const expenseTrendData = chartData.monthlyTrend || [];

    const hasExpenseData = expenseTrendData.some(
        item => Number(item.expenses) > 0
    );

    if (
        expenseTrendCanvas &&
        expenseTrendWrapper &&
        expenseTrendEmpty
    ) {
        if (!hasExpenseData) {
            expenseTrendWrapper.hidden = true;
            expenseTrendEmpty.hidden = false;
        } else {
            new Chart(expenseTrendCanvas, {
                type: "line",

                data: {
                    labels: expenseTrendData.map(
                        item => item.label
                    ),

                    datasets: [
                        {
                            label: "Monthly Expenses",

                            data: expenseTrendData.map(
                                item => item.expenses
                            ),

                            borderColor:
                                "rgba(249, 115, 22, 1)",

                            backgroundColor:
                                "rgba(249, 115, 22, 0.12)",

                            pointBackgroundColor:
                                "rgba(249, 115, 22, 1)",

                            pointBorderColor:
                                "rgba(249, 115, 22, 1)",

                            borderWidth: 3,
                            pointRadius: 5,
                            pointHoverRadius: 7,
                            tension: 0.3,
                            fill: true
                        }
                    ]
                },

                options: {
                    ...sharedOptions,

                    plugins: {
                        ...sharedOptions.plugins,

                        tooltip: {
                            callbacks: {
                                label(context) {
                                    return (
                                        "Monthly Expenses: " +
                                        `¥${Number(
                                            context.raw
                                        ).toLocaleString()}`
                                    );
                                }
                            }
                        }
                    }
                }
            });
        }
    }
}