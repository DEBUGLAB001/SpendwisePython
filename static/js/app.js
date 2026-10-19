// SpendWise Application Logic
document.addEventListener("DOMContentLoaded", () => {
    // State
    const state = {
        activeTab: "overview",
        categories: [],
        transactions: [],
        pagination: {
            page: 1,
            per_page: 8,
            total_count: 0,
            total_pages: 1
        },
        filters: {
            search: "",
            category: "all",
            start_date: "",
            end_date: "",
            sort_by: "date",
            direction: "desc"
        },
        deleteTxId: null
    };

    // DOM Elements
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const pageTitle = document.getElementById("page-title");

    // Modal Elements
    const expenseModal = document.getElementById("expense-modal");
    const deleteModal = document.getElementById("delete-modal");
    const formExpense = document.getElementById("form-expense");
    const formUpdateBudget = document.getElementById("form-update-budget");
    const btnAddExpense = document.getElementById("btn-add-expense");
    const btnQuickBudget = document.getElementById("btn-quick-budget");
    const btnModalClose = document.getElementById("btn-modal-close");
    const btnModalCancel = document.getElementById("btn-modal-cancel");
    const btnDelModalClose = document.getElementById("btn-del-modal-close");
    const btnDelCancel = document.getElementById("btn-del-cancel");
    const btnDelConfirm = document.getElementById("btn-del-confirm");
    const btnClearFilters = document.getElementById("btn-clear-filters");
    const btnViewAllTx = document.getElementById("btn-view-all-tx");
    const btnPrevPage = document.getElementById("btn-prev-page");
    const btnNextPage = document.getElementById("btn-next-page");

    // Inputs
    const txSearchInput = document.getElementById("tx-search-input");
    const txCategorySelect = document.getElementById("tx-category-select");
    const txDateFrom = document.getElementById("tx-date-from");
    const txDateTo = document.getElementById("tx-date-to");
    const txSortSelect = document.getElementById("tx-sort-select");
    const expCategorySelect = document.getElementById("exp-category");

    // Formatters
    const formatCurrency = (amount) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD"
        }).format(amount || 0);
    };

    // Toast Notification System
    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(100%)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // Tab Switching
    function switchTab(tabId) {
        state.activeTab = tabId;

        navItems.forEach(btn => {
            btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
        });

        tabPanes.forEach(pane => {
            pane.classList.toggle("active", pane.id === `pane-${tabId}`);
        });

        const titles = {
            overview: "Financial Overview",
            transactions: "Transaction History",
            budgets: "Budget Management",
            analytics: "Spending Analytics"
        };
        pageTitle.textContent = titles[tabId] || "SpendWise";

        // Refresh relevant data
        if (tabId === "overview") loadOverview();
        if (tabId === "transactions") loadTransactions();
        if (tabId === "budgets") loadBudgets();
        if (tabId === "analytics") loadAnalytics();
    }

    navItems.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.getAttribute("data-tab");
            switchTab(target);
        });
    });

    if (btnViewAllTx) {
        btnViewAllTx.addEventListener("click", () => switchTab("transactions"));
    }

    if (btnQuickBudget) {
        btnQuickBudget.addEventListener("click", () => switchTab("budgets"));
    }

    // Load Categories
    async function loadCategories() {
        try {
            const res = await fetch("/api/categories");
            if (!res.ok) throw new Error("Failed to load categories");
            const data = await res.json();
            state.categories = data.categories || [];

            // Populate filters
            txCategorySelect.innerHTML = `<option value="all">All Categories</option>`;
            expCategorySelect.innerHTML = "";

            state.categories.forEach(cat => {
                const opt1 = document.createElement("option");
                opt1.value = cat;
                opt1.textContent = cat;
                txCategorySelect.appendChild(opt1);

                const opt2 = document.createElement("option");
                opt2.value = cat;
                opt2.textContent = cat;
                expCategorySelect.appendChild(opt2);
            });
        } catch (err) {
            console.error(err);
        }
    }

    // 1. Overview Tab
    async function loadOverview() {
        try {
            const res = await fetch("/api/summary");
            if (!res.ok) throw new Error("Failed to load summary");
            const data = await res.json();

            // Populate Cards
            document.getElementById("card-total-spent").textContent = formatCurrency(data.total_spent);
            document.getElementById("card-total-count").textContent = `${data.transaction_count} recorded expenses`;
            document.getElementById("card-remaining-budget").textContent = formatCurrency(data.budget.remaining);
            document.getElementById("card-budget-limit").textContent = formatCurrency(data.budget.budget_limit);
            document.getElementById("card-utilization-text").textContent = `${data.budget.utilization_percentage}% allocated`;

            const topCat = data.highest_category || { category: "None", amount: 0 };
            document.getElementById("card-top-category").textContent = topCat.category;
            document.getElementById("card-top-category-amount").textContent = formatCurrency(topCat.amount);

            // Badges & Alert Banner
            const statusBadge = document.getElementById("card-budget-status-badge");
            statusBadge.textContent = data.budget.status.toUpperCase();
            statusBadge.className = `badge ${data.budget.status}`;

            const banner = document.getElementById("budget-alert-banner");
            const bannerTitle = document.getElementById("budget-alert-title");
            const bannerDesc = document.getElementById("budget-alert-desc");
            const bannerFill = document.getElementById("overview-budget-fill");

            const fillWidth = Math.min(100, data.budget.utilization_percentage);
            bannerFill.style.width = `${fillWidth}%`;
            bannerFill.className = `progress-bar-fill ${data.budget.status === 'exceeded' ? 'danger' : data.budget.status === 'warning' ? 'warn' : ''}`;

            if (data.budget.status === "exceeded") {
                bannerTitle.textContent = "Budget Ceilings Exceeded";
                bannerDesc.textContent = data.budget.message;
            } else if (data.budget.status === "warning") {
                bannerTitle.textContent = "Caution: Approaching Budget Limit";
                bannerDesc.textContent = data.budget.message;
            } else {
                bannerTitle.textContent = "Budget In Good Standing";
                bannerDesc.textContent = data.budget.message;
            }

            // Sidebar mini card
            document.getElementById("sidebar-budget-val").textContent = formatCurrency(data.budget.budget_limit);
            const sideFill = document.getElementById("sidebar-budget-fill");
            sideFill.style.width = `${fillWidth}%`;
            sideFill.className = `progress-bar-fill ${data.budget.status === 'exceeded' ? 'danger' : data.budget.status === 'warning' ? 'warn' : ''}`;
            document.getElementById("sidebar-budget-sub").textContent = `${data.budget.utilization_percentage}% utilized`;

            // Recent Transactions Table
            const recentTbody = document.getElementById("overview-recent-tbody");
            if (data.recent_transactions && data.recent_transactions.length > 0) {
                recentTbody.innerHTML = data.recent_transactions.map(t => `
                    <tr>
                        <td class="muted">${t.date}</td>
                        <td class="font-medium">${escapeHtml(t.description)}</td>
                        <td><span class="category-tag">${escapeHtml(t.category)}</span></td>
                        <td class="text-right amount-cell">${formatCurrency(t.amount)}</td>
                    </tr>
                `).join("");
            } else {
                recentTbody.innerHTML = `<tr><td colspan="4" class="text-center muted py-4">No recent expenses found.</td></tr>`;
            }

            // Category Breakdown Progress Bars
            const catContainer = document.getElementById("overview-category-list");
            if (data.categories && data.categories.length > 0) {
                catContainer.innerHTML = data.categories.slice(0, 6).map(c => `
                    <div class="cat-row">
                        <div class="cat-row-info">
                            <span class="cat-name">${escapeHtml(c.category)}</span>
                            <span class="cat-meta">${formatCurrency(c.total_amount)} (${c.percentage}%)</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: ${c.percentage}%;"></div>
                        </div>
                    </div>
                `).join("");
            } else {
                catContainer.innerHTML = `<div class="text-center muted py-4">No category data available.</div>`;
            }
        } catch (err) {
            console.error("Overview error:", err);
            showToast("Failed to load overview summary", "error");
        }
    }

    // 2. Transactions Tab
    async function loadTransactions() {
        const tbody = document.getElementById("tx-table-body");
        tbody.innerHTML = `<tr><td colspan="6" class="text-center muted py-4">Loading transactions...</td></tr>`;

        try {
            const params = new URLSearchParams({
                page: state.pagination.page,
                per_page: state.pagination.per_page,
                search: state.filters.search,
                category: state.filters.category,
                start_date: state.filters.start_date,
                end_date: state.filters.end_date,
                sort_by: state.filters.sort_by,
                direction: state.filters.direction
            });

            const res = await fetch(`/api/transactions?${params.toString()}`);
            if (!res.ok) throw new Error("Failed to fetch transactions");
            const data = await res.json();

            state.transactions = data.items || [];
            state.pagination.page = data.page;
            state.pagination.total_count = data.total_count;
            state.pagination.total_pages = data.total_pages;

            renderTransactionsTable();
            updatePaginationUI();
        } catch (err) {
            console.error("Transactions error:", err);
            tbody.innerHTML = `<tr><td colspan="6" class="text-center muted py-4">Error loading transactions.</td></tr>`;
            showToast("Failed to fetch transactions", "error");
        }
    }

    function renderTransactionsTable() {
        const tbody = document.getElementById("tx-table-body");
        if (state.transactions.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center muted py-4">No matching transactions found. Try adjusting your search or filters.</td></tr>`;
            return;
        }

        tbody.innerHTML = state.transactions.map(t => `
            <tr data-id="${t.id}">
                <td class="muted">${t.date}</td>
                <td class="font-medium">${escapeHtml(t.description)}</td>
                <td><span class="category-tag">${escapeHtml(t.category)}</span></td>
                <td class="muted text-sm">${escapeHtml(t.notes || "—")}</td>
                <td class="text-right amount-cell">${formatCurrency(t.amount)}</td>
                <td class="text-center">
                    <button class="btn btn-text btn-sm btn-edit-tx" data-id="${t.id}">Edit</button>
                    <button class="btn btn-text btn-sm text-danger btn-del-tx" data-id="${t.id}" style="color: var(--accent-rose);">Delete</button>
                </td>
            </tr>
        `).join("");

        // Attach action handlers
        document.querySelectorAll(".btn-edit-tx").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                openEditModal(id);
            });
        });

        document.querySelectorAll(".btn-del-tx").forEach(btn => {
            btn.addEventListener("click", () => {
                const id = btn.getAttribute("data-id");
                openDeleteModal(id);
            });
        });
    }

    function updatePaginationUI() {
        const info = document.getElementById("pagination-info");
        const indicator = document.getElementById("page-indicator");

        info.textContent = `Showing ${state.transactions.length} of ${state.pagination.total_count} transactions`;
        indicator.textContent = `Page ${state.pagination.page} of ${state.pagination.total_pages}`;

        btnPrevPage.disabled = (state.pagination.page <= 1);
        btnNextPage.disabled = (state.pagination.page >= state.pagination.total_pages);
    }

    // Filter controls
    let searchDebounce = null;
    txSearchInput.addEventListener("input", (e) => {
        clearTimeout(searchDebounce);
        searchDebounce = setTimeout(() => {
            state.filters.search = e.target.value;
            state.pagination.page = 1;
            loadTransactions();
        }, 300);
    });

    txCategorySelect.addEventListener("change", (e) => {
        state.filters.category = e.target.value;
        state.pagination.page = 1;
        loadTransactions();
    });

    txDateFrom.addEventListener("change", (e) => {
        state.filters.start_date = e.target.value;
        state.pagination.page = 1;
        loadTransactions();
    });

    txDateTo.addEventListener("change", (e) => {
        state.filters.end_date = e.target.value;
        state.pagination.page = 1;
        loadTransactions();
    });

    txSortSelect.addEventListener("change", (e) => {
        const val = e.target.value;
        const [sort_by, direction] = val.split("_");
        state.filters.sort_by = sort_by;
        state.filters.direction = direction;
        state.pagination.page = 1;
        loadTransactions();
    });

    btnClearFilters.addEventListener("click", () => {
        txSearchInput.value = "";
        txCategorySelect.value = "all";
        txDateFrom.value = "";
        txDateTo.value = "";
        txSortSelect.value = "date_desc";

        state.filters = {
            search: "",
            category: "all",
            start_date: "",
            end_date: "",
            sort_by: "date",
            direction: "desc"
        };
        state.pagination.page = 1;
        loadTransactions();
        showToast("Filters reset", "info");
    });

    btnPrevPage.addEventListener("click", () => {
        if (state.pagination.page > 1) {
            state.pagination.page--;
            loadTransactions();
        }
    });

    btnNextPage.addEventListener("click", () => {
        if (state.pagination.page < state.pagination.total_pages) {
            state.pagination.page++;
            loadTransactions();
        }
    });

    // 3. Budgets Tab
    async function loadBudgets() {
        try {
            const res = await fetch("/api/budget");
            if (!res.ok) throw new Error("Failed to load budget data");
            const data = await res.json();

            document.getElementById("budget-view-limit").textContent = formatCurrency(data.budget_limit);
            document.getElementById("budget-view-spent").textContent = formatCurrency(data.total_spent);
            document.getElementById("budget-view-remaining").textContent = formatCurrency(data.remaining);
            document.getElementById("budget-view-percentage").textContent = `${data.utilization_percentage}%`;

            const pill = document.getElementById("budget-status-pill");
            pill.textContent = data.status.toUpperCase();
            pill.className = `budget-badge-large ${data.status}`;

            document.getElementById("budget-meter-label").textContent = `${data.utilization_percentage}% of target`;
            const meterFill = document.getElementById("budget-view-meter-fill");
            const fillWidth = Math.min(100, data.utilization_percentage);
            meterFill.style.width = `${fillWidth}%`;
            meterFill.className = `progress-bar-fill ${data.status === 'exceeded' ? 'danger' : data.status === 'warning' ? 'warn' : ''}`;

            // Pre-fill input
            document.getElementById("input-new-budget").value = data.budget_limit;
            document.getElementById("budget-feedback").textContent = "";
        } catch (err) {
            console.error("Budget view error:", err);
            showToast("Failed to load budget status", "error");
        }
    }

    formUpdateBudget.addEventListener("submit", async (e) => {
        e.preventDefault();
        const feedback = document.getElementById("budget-feedback");
        const amountVal = parseFloat(document.getElementById("input-new-budget").value);

        if (isNaN(amountVal) || amountVal <= 0) {
            feedback.className = "form-feedback error";
            feedback.textContent = "Please enter a valid positive budget amount.";
            return;
        }

        feedback.className = "form-feedback";
        feedback.textContent = "Updating budget...";

        try {
            // Frontend payload sends { amount: amountVal }
            const res = await fetch("/api/budget", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ amount: amountVal })
            });

            const data = await res.json();
            if (!res.ok) {
                feedback.className = "form-feedback error";
                feedback.textContent = data.error || "Failed to update budget";
                showToast(`Budget update failed: ${data.error || 'Server error'}`, "error");
                return;
            }

            feedback.className = "form-feedback success";
            feedback.textContent = "Monthly budget updated successfully.";
            showToast("Monthly budget updated successfully", "success");
            loadBudgets();
            loadOverview();
        } catch (err) {
            console.error("Update budget error:", err);
            feedback.className = "form-feedback error";
            feedback.textContent = "A network or communication error occurred.";
            showToast("Failed to communicate with budget server", "error");
        }
    });

    // 4. Analytics Tab
    async function loadAnalytics() {
        try {
            const res = await fetch("/api/analytics");
            if (!res.ok) throw new Error("Failed to load analytics");
            const data = await res.json();

            // Monthly Chart (Rendered via clean CSS bar columns)
            const chartContainer = document.getElementById("monthly-chart-container");
            const monthlyData = data.monthly_comparison || [];

            if (monthlyData.length > 0) {
                const maxSpend = Math.max(...monthlyData.map(m => m.total), 1);
                chartContainer.innerHTML = monthlyData.map(m => {
                    const heightPercent = Math.max(8, Math.round((m.total / maxSpend) * 160));
                    return `
                        <div class="bar-col">
                            <span class="bar-val">${formatCurrency(m.total)}</span>
                            <div class="bar-rect" style="height: ${heightPercent}px;"></div>
                            <span class="bar-label">${m.month}</span>
                        </div>
                    `;
                }).join("");
            } else {
                chartContainer.innerHTML = `<div class="text-center muted py-4">No monthly data available.</div>`;
            }

            // Category Allocation
            const catList = document.getElementById("analytics-category-list");
            const categories = data.categories || [];
            if (categories.length > 0) {
                catList.innerHTML = categories.map(c => `
                    <div class="cat-row">
                        <div class="cat-row-info">
                            <span class="cat-name">${escapeHtml(c.category)} (${c.transaction_count} items)</span>
                            <span class="cat-meta">${formatCurrency(c.total_amount)} — ${c.percentage}%</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: ${c.percentage}%;"></div>
                        </div>
                    </div>
                `).join("");
            } else {
                catList.innerHTML = `<div class="text-center muted py-4">No category data recorded.</div>`;
            }

            // Insights
            const allTxs = (await (await fetch("/api/transactions?per_page=100")).json()).items || [];
            if (allTxs.length > 0) {
                const total = allTxs.reduce((sum, t) => sum + t.amount, 0);
                const avg = total / allTxs.length;
                const maxTx = allTxs.reduce((prev, curr) => (curr.amount > prev.amount) ? curr : prev, allTxs[0]);
                const uniqueCats = new Set(allTxs.map(t => t.category)).size;

                document.getElementById("insight-avg-tx").textContent = formatCurrency(avg);
                document.getElementById("insight-max-tx").textContent = formatCurrency(maxTx.amount);
                document.getElementById("insight-max-desc").textContent = maxTx.description;
                document.getElementById("insight-cat-count").textContent = uniqueCats;
            }
        } catch (err) {
            console.error("Analytics error:", err);
            showToast("Failed to load analytics", "error");
        }
    }

    // Modal Operations (Add / Edit)
    function openAddModal() {
        document.getElementById("expense-modal-title").textContent = "Record New Expense";
        document.getElementById("expense-edit-id").value = "";
        document.getElementById("exp-description").value = "";
        document.getElementById("exp-amount").value = "";
        document.getElementById("exp-date").value = new Date().toISOString().split("T")[0];
        document.getElementById("exp-notes").value = "";
        document.getElementById("expense-form-feedback").textContent = "";
        expenseModal.classList.add("active");
    }

    async function openEditModal(id) {
        try {
            const res = await fetch(`/api/transactions/${id}`);
            if (!res.ok) throw new Error("Could not find transaction");
            const tx = await res.json();

            document.getElementById("expense-modal-title").textContent = "Edit Expense";
            document.getElementById("expense-edit-id").value = tx.id;
            document.getElementById("exp-description").value = tx.description;
            document.getElementById("exp-amount").value = tx.amount;
            document.getElementById("exp-category").value = tx.category;
            document.getElementById("exp-date").value = tx.date;
            document.getElementById("exp-notes").value = tx.notes || "";
            document.getElementById("expense-form-feedback").textContent = "";

            expenseModal.classList.add("active");
        } catch (err) {
            console.error("Edit modal error:", err);
            showToast("Failed to load transaction details", "error");
        }
    }

    function closeExpenseModal() {
        expenseModal.classList.remove("active");
    }

    btnAddExpense.addEventListener("click", openAddModal);
    btnModalClose.addEventListener("click", closeExpenseModal);
    btnModalCancel.addEventListener("click", closeExpenseModal);

    // Form Submit (Add or Edit)
    formExpense.addEventListener("submit", async (e) => {
        e.preventDefault();
        const feedback = document.getElementById("expense-form-feedback");
        const editId = document.getElementById("expense-edit-id").value;

        const payload = {
            description: document.getElementById("exp-description").value.trim(),
            amount: parseFloat(document.getElementById("exp-amount").value),
            category: document.getElementById("exp-category").value,
            date: document.getElementById("exp-date").value,
            notes: document.getElementById("exp-notes").value.trim()
        };

        if (!payload.description) {
            feedback.className = "modal-feedback error";
            feedback.textContent = "Description is required.";
            return;
        }

        if (isNaN(payload.amount) || payload.amount <= 0) {
            feedback.className = "modal-feedback error";
            feedback.textContent = "Amount must be a positive number greater than 0.";
            return;
        }

        const isEdit = Boolean(editId);
        const url = isEdit ? `/api/transactions/${editId}` : "/api/transactions";
        const method = isEdit ? "PUT" : "POST";

        try {
            const res = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) {
                feedback.className = "modal-feedback error";
                feedback.textContent = data.error || "Submission failed";
                return;
            }

            closeExpenseModal();
            showToast(isEdit ? "Transaction updated successfully" : "Expense recorded successfully", "success");
            
            // Refresh views
            if (state.activeTab === "overview") loadOverview();
            if (state.activeTab === "transactions") loadTransactions();
            if (state.activeTab === "budgets") loadBudgets();
            if (state.activeTab === "analytics") loadAnalytics();
        } catch (err) {
            console.error("Expense submit error:", err);
            feedback.className = "modal-feedback error";
            feedback.textContent = "Server communication failed.";
        }
    });

    // Delete Modal
    function openDeleteModal(id) {
        state.deleteTxId = id;
        const tx = state.transactions.find(t => t.id == id);
        const descEl = document.getElementById("delete-tx-desc");
        descEl.textContent = tx ? `"${tx.description}"` : "this transaction";
        deleteModal.classList.add("active");
    }

    function closeDeleteModal() {
        state.deleteTxId = null;
        deleteModal.classList.remove("active");
    }

    btnDelModalClose.addEventListener("click", closeDeleteModal);
    btnDelCancel.addEventListener("click", closeDeleteModal);

    btnDelConfirm.addEventListener("click", async () => {
        if (!state.deleteTxId) return;

        try {
            const res = await fetch(`/api/transactions/${state.deleteTxId}`, {
                method: "DELETE"
            });

            const data = await res.json();
            if (!res.ok) {
                showToast(data.error || "Failed to delete transaction", "error");
                closeDeleteModal();
                return;
            }

            closeDeleteModal();
            showToast("Transaction deleted successfully", "success");

            // Refresh views
            if (state.activeTab === "transactions") loadTransactions();
            if (state.activeTab === "overview") loadOverview();
            if (state.activeTab === "budgets") loadBudgets();
            if (state.activeTab === "analytics") loadAnalytics();
        } catch (err) {
            console.error("Delete error:", err);
            showToast("Network error deleting transaction", "error");
            closeDeleteModal();
        }
    });

    // Helper: Escape HTML
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initialize
    async function init() {
        await loadCategories();
        switchTab("overview");
    }

    init();
});
