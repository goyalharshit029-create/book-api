const API = "";

// ======================================
// PROFESSIONAL TOAST NOTIFICATIONS
// ======================================

function showToast(message, type = "success") {

    const icons = {
        success: "bi-check-circle-fill",
        error: "bi-x-circle-fill",
        warning: "bi-exclamation-triangle-fill",
        info: "bi-info-circle-fill"
    };

    let container =
        document.getElementById("toastContainer");

    if (!container) {

        container = document.createElement("div");

        container.id = "toastContainer";

        container.className =
            "toast-container position-fixed top-0 end-0 p-3";

        document.body.appendChild(container);

    }

    const toastId =
        "toast-" + Date.now();

    const toast = document.createElement("div");

    toast.id = toastId;

    toast.className =
        `custom-toast ${type}`;

    toast.innerHTML = `

        <div class="toast-icon">
            <i class="bi ${icons[type]}"></i>
        </div>

        <div class="toast-message">
            ${message}
        </div>

        <button
            type="button"
            class="toast-close"
            aria-label="Close">

            <i class="bi bi-x-lg"></i>

        </button>
    `;

    container.appendChild(toast);

    const removeToast = () => {

        toast.classList.add("hide-toast");

        setTimeout(() => {
            toast.remove();
        }, 300);

    };

    toast
        .querySelector(".toast-close")
        .addEventListener("click", removeToast);

    setTimeout(removeToast, 3500);

}

let currentPage = 1;
let pageSize = 10;
let totalPages = 1;

let issuedBooksData = [];
let issuedCurrentPage = 1;
let issuedTotalPages = 1;
const issuedPageSize = 5;


// ======================================
// AUTH CHECK
// ======================================

function checkAuth() {
    if (window.location.pathname === "/dashboard") {
        const token = localStorage.getItem("token");

        if (!token) {
            showToast("Please login first.", "warning");
            window.location.href = "/login-page";
        }
    }
}

checkAuth();


// ======================================
// REGISTER
// ======================================

async function registerUser() {
    const username = document.getElementById("username")?.value.trim();
    const email = document.getElementById("email")?.value.trim();
    const password = document.getElementById("password")?.value.trim();

    if (!username || !email || !password) {
        showToast("Please fill all fields.", "warning");
        return;
    }

    try {
        const response = await fetch(API + "/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const data = await response.json();

        if (response.ok) {
            showToast("Registration successful!", "success");
            window.location.href = "/login-page";
        } else {
            showToast(data.detail || "Registration failed.", "error");
        }

    } catch (error) {
        console.error("Registration error:", error);
        showToast("Something went wrong during registration.", "error");
    }
}


// ======================================
// LOGIN
// ======================================

async function loginUser() {
    const email = document.getElementById("email")?.value.trim();
    const password = document.getElementById("password")?.value.trim();

    if (!email || !password) {
        showToast("Please enter Email and Password.", "warning");
        return;
    }

    try {
        const form = new URLSearchParams();

        form.append("username", email);
        form.append("password", password);

        const response = await fetch(API + "/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: form
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("role", data.role);

            console.log("Logged in role:", data.role);

            showToast("Login successful!", "success");
            window.location.href = "/dashboard";

        } else {
            showToast(data.detail || "Invalid credentials.", "error");
        }

    } catch (error) {
        console.error("Login error:", error);
        showToast("Something went wrong while logging in.", "error");
    }
}


// ======================================
// LOGOUT
// ======================================

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");

    window.location.href = "/login-page";
}


// ======================================
// LOAD BOOKS
// ======================================

async function loadBooks(page = 1) {
    const table = document.getElementById("bookTable");

    if (!table) return;

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    try {
        const response = await fetch(
            API + `/books?page=${page}&page_size=${pageSize}`,
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            throw new Error("Unable to load books");
        }

        const data = await response.json();

        currentPage = data.page || 1;
        totalPages = data.total_pages || 1;

        const books = data.books || [];

        const head = document.getElementById("bookTableHead");

        if (head) {
            if (role === "admin") {
                head.innerHTML = `
                    <tr>
                        <th>Title</th>
                        <th>Author</th>
                        <th>Genre</th>
                        <th>Price</th>
                        <th>Year</th>
                        <th>Actions</th>
                    </tr>
                `;
            } else {
                head.innerHTML = `
                    <tr>
                        <th>Title</th>
                        <th>Author</th>
                        <th>Genre</th>
                        <th>Price</th>
                        <th>Year</th>
                    </tr>
                `;
            }
        }

        table.innerHTML = "";

        if (books.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="${role === "admin" ? 6 : 5}" class="text-center">
                        No books found.
                    </td>
                </tr>
            `;
        }

        books.forEach(book => {
            if (role === "admin") {
                table.innerHTML += `
                    <tr>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.genre}</td>
                        <td>₹${book.price}</td>
                        <td>${book.published_year}</td>
                        <td>
                            <button
                                class="btn btn-warning btn-sm me-2"
                                onclick="editBook(${book.id})">
                                ✏️
                            </button>

                            <button
                                class="btn btn-danger btn-sm"
                                onclick="deleteBook(${book.id})">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `;
            } else {
                table.innerHTML += `
                    <tr>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.genre}</td>
                        <td>₹${book.price}</td>
                        <td>${book.published_year}</td>
                    </tr>
                `;
            }
        });

        updatePagination();

    } catch (error) {
        console.error("Load books error:", error);
        showToast("Unable to load books.", "error");
    }
}


// ======================================
// BOOK PAGINATION
// ======================================

function updatePagination() {
    const pagination = document.getElementById("pagination");

    if (!pagination) return;

    pagination.innerHTML = `
        <button
            class="btn btn-outline-primary me-2"
            onclick="loadBooks(${currentPage - 1})"
            ${currentPage <= 1 ? "disabled" : ""}>
            ← Previous
        </button>

        <span class="fw-bold mx-2">
            Page ${currentPage} of ${totalPages}
        </span>

        <button
            class="btn btn-outline-primary ms-2"
            onclick="loadBooks(${currentPage + 1})"
            ${currentPage >= totalPages ? "disabled" : ""}>
            Next →
        </button>
    `;
}


// ======================================
// SEARCH BOOKS
// ======================================

async function searchBooks() {
    const searchInput = document.getElementById("search");
    const table = document.getElementById("bookTable");

    if (!searchInput || !table) return;

    const keyword = searchInput.value
        .toLowerCase()
        .trim();

    if (keyword === "") {
        loadBooks(1);
        return;
    }

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    try {
        const response = await fetch(
            API + "/books?page=1&page_size=100",
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            throw new Error("Search failed");
        }

        const data = await response.json();

        const books = data.books || [];

        const filteredBooks = books.filter(book =>
            (book.title || "").toLowerCase().includes(keyword) ||
            (book.author || "").toLowerCase().includes(keyword) ||
            (book.genre || "").toLowerCase().includes(keyword)
        );

        table.innerHTML = "";

        if (filteredBooks.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="${role === "admin" ? 6 : 5}" class="text-center">
                        No matching books found.
                    </td>
                </tr>
            `;
        }

        filteredBooks.forEach(book => {
            if (role === "admin") {
                table.innerHTML += `
                    <tr>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.genre}</td>
                        <td>₹${book.price}</td>
                        <td>${book.published_year}</td>
                        <td>
                            <button
                                class="btn btn-warning btn-sm me-2"
                                onclick="editBook(${book.id})">
                                ✏️
                            </button>

                            <button
                                class="btn btn-danger btn-sm"
                                onclick="deleteBook(${book.id})">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `;
            } else {
                table.innerHTML += `
                    <tr>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.genre}</td>
                        <td>₹${book.price}</td>
                        <td>${book.published_year}</td>
                    </tr>
                `;
            }
        });

        const pagination = document.getElementById("pagination");

        if (pagination) {
            pagination.innerHTML = "";
        }

    } catch (error) {
        console.error("Search error:", error);
    }
}


// ======================================
// ADD / UPDATE BOOK
// ======================================

async function addBook() {
    const title = document.getElementById("title")?.value.trim();
    const author = document.getElementById("author")?.value.trim();
    const genre = document.getElementById("genre")?.value.trim();

    const price = parseFloat(
        document.getElementById("price")?.value
    );

    const published_year = parseInt(
        document.getElementById("year")?.value
    );

    if (
        !title ||
        !author ||
        !genre ||
        Number.isNaN(price) ||
        Number.isNaN(published_year)
    ) {
        showToast("Please fill all fields correctly.", "warning");
        return;
    }

    const token = localStorage.getItem("token");

    const isEditing = !!window.currentBookId;

    try {
        const response = await fetch(
            isEditing
                ? API + "/books/" + window.currentBookId
                : API + "/books",
            {
                method: isEditing ? "PUT" : "POST",

                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + token
                },

                body: JSON.stringify({
                    title,
                    author,
                    genre,
                    price,
                    published_year
                })
            }
        );

        const data = await response.json();

        if (response.ok) {
            showToast(
                isEditing
                    ? "Book updated successfully!"
                    : "Book added successfully!",
                "success"
            );

            document.getElementById("title").value = "";
            document.getElementById("author").value = "";
            document.getElementById("genre").value = "";
            document.getElementById("price").value = "";
            document.getElementById("year").value = "";

            window.currentBookId = null;

            const saveButton = document.querySelector(
                "#addBookModal .btn-success"
            );

            if (saveButton) {
                saveButton.innerText = "Save Book";
            }

            await loadBooks(currentPage);

            const modalElement =
                document.getElementById("addBookModal");

            const modal =
                bootstrap.Modal.getInstance(modalElement);

            if (modal) {
                modal.hide();
            }

        } else {
            showToast(data.detail || "Operation failed.", "error");
        }

    } catch (error) {
        console.error("Add/Update book error:", error);
        showToast("Something went wrong.", "error");
    }

    await loadBooks(currentPage);
    await loadStats();
}


// ======================================
// DELETE BOOK
// ======================================

async function deleteBook(id) {
    const ok = confirm(
        "Are you sure you want to delete this book?"
    );

    if (!ok) return;

    const token = localStorage.getItem("token");

    try {
        const response = await fetch(
            API + "/books/" + id,
            {
                method: "DELETE",
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        );

        if (response.ok) {
            showToast("Book deleted successfully!", "success");

            if (
                currentPage > 1 &&
                document.querySelectorAll("#bookTable tr").length <= 1
            ) {
                currentPage--;
            }

            loadBooks(currentPage);

        } else {
            const data = await response.json();

            showToast(data.detail || "Delete failed.", "error");
        }

    } catch (error) {
        console.error("Delete book error:", error);
        showToast("Something went wrong.", "error");
    }

    await loadBooks(currentPage);
    await loadStats();
}


// ======================================
// EDIT BOOK
// ======================================

async function editBook(id) {
    const token = localStorage.getItem("token");

    try {
        const response = await fetch(
            API + "/books/" + id,
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            showToast("Unable to fetch book details.", "error");
            return;
        }

        const book = await response.json();

        document.getElementById("title").value = book.title || "";
        document.getElementById("author").value = book.author || "";
        document.getElementById("genre").value = book.genre || "";
        document.getElementById("price").value = book.price || "";
        document.getElementById("year").value =
            book.published_year || "";

        window.currentBookId = id;

        const saveButton = document.querySelector(
            "#addBookModal .btn-success"
        );

        if (saveButton) {
            saveButton.innerText = "Update Book";
        }

        const modalElement =
            document.getElementById("addBookModal");

        const modal = new bootstrap.Modal(modalElement);

        modal.show();

    } catch (error) {
        console.error("Edit book error:", error);
        showToast("Something went wrong.", "error");
    }
}


// ======================================
// CONTACT
// ======================================

async function sendContact() {
    const name =
        document.getElementById("contactName")?.value.trim();

    const email =
        document.getElementById("contactEmail")?.value.trim();

    const subject =
        document.getElementById("contactSubject")?.value.trim();

    const message =
        document.getElementById("contactMessage")?.value.trim();

    if (!name || !email || !subject || !message) {
        showToast("Please fill all fields.", "warning");
        return;
    }

    try {
        const response = await fetch(
            API + "/contact",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    name,
                    email,
                    subject,
                    message
                })
            }
        );

        const data = await response.json();

        if (response.ok) {
            showToast("Message sent successfully!", "success");

            document.getElementById("contactName").value = "";
            document.getElementById("contactEmail").value = "";
            document.getElementById("contactSubject").value = "";
            document.getElementById("contactMessage").value = "";

            if (typeof loadStats === "function") {
                loadStats();
            }

        } else {
            showToast(data.detail || "Failed to send message.", "error");
        }

    } catch (error) {
        console.error("Contact error:", error);
        showToast("Something went wrong.", "error");
    }
}


// ======================================
// LOAD ISSUED BOOKS
// ======================================

async function loadMyIssuedBooks(page = 1) {
    const table =
        document.getElementById("issuedBookTable");

    if (!table) return;

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // ======================================
    // DASHBOARD CARDS
    // ======================================

    const totalBooksCard =
        document.getElementById("totalBooksCard");

    const totalUsersCard =
        document.getElementById("totalUsersCard");

    const totalContactsCard =
        document.getElementById("totalContactsCard");

    const myIssuedBooksCard =
        document.getElementById("myIssuedBooksCard");

    if (role === "admin") {
        totalBooksCard?.classList.remove("d-none");
        totalUsersCard?.classList.remove("d-none");
        totalContactsCard?.classList.remove("d-none");
        myIssuedBooksCard?.classList.add("d-none");
    } else {
        totalBooksCard?.classList.add("d-none");
        totalUsersCard?.classList.add("d-none");
        totalContactsCard?.classList.add("d-none");
        myIssuedBooksCard?.classList.remove("d-none");
    }


    // ======================================
    // TABLE HEADINGS
    // ======================================

    const head =
        document.getElementById("issuedBookHead");

    if (head) {
        if (role === "admin") {
            head.innerHTML = `
                <tr>
                    <th>Book Title</th>
                    <th>Author</th>
                    <th>Student</th>
                    <th>Issue Date</th>
                    <th>Due Date</th>
                    <th>Fine</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            `;
        } else {
            head.innerHTML = `
                <tr>
                    <th>Book Title</th>
                    <th>Author</th>
                    <th>Issue Date</th>
                    <th>Due Date</th>
                    <th>Fine</th>
                    <th>Status</th>
                </tr>
            `;
        }
    }


    table.innerHTML = `
        <tr>
            <td
                colspan="${role === "admin" ? 8 : 6}"
                class="text-center">
                Loading issued books...
            </td>
        </tr>
    `;


    try {
        const endpoint =
            role === "admin"
                ? "/issued-books"
                : "/my-issued-books";

        const response = await fetch(
            API + endpoint,
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            throw new Error(
                "Failed to load issued books"
            );
        }

        let data = await response.json();

        // Supports both array response
        // and paginated object response
        let issuedBooks = Array.isArray(data)
            ? data
            : (data.books || data.issued_books || []);

        // Show only active issued books
        issuedBooks = issuedBooks.filter(book =>
            (book.status || "")
                .toLowerCase() === "issued"
        );

        // Store full data for search
        issuedBooksData = issuedBooks;


        // ======================================
        // PAGINATION
        // ======================================

        issuedTotalPages = Math.max(
            1,
            Math.ceil(
                issuedBooks.length / issuedPageSize
            )
        );

        if (page < 1) page = 1;

        if (page > issuedTotalPages) {
            page = issuedTotalPages;
        }

        issuedCurrentPage = page;

        const startIndex =
            (issuedCurrentPage - 1) *
            issuedPageSize;

        const paginatedBooks =
            issuedBooks.slice(
                startIndex,
                startIndex + issuedPageSize
            );


        table.innerHTML = "";

        if (issuedBooks.length === 0) {
            table.innerHTML = `
                <tr>
                    <td
                        colspan="${role === "admin" ? 8 : 6}"
                        class="text-center text-muted">
                        No issued books found.
                    </td>
                </tr>
            `;
        } else {
            renderIssuedBooks(
                paginatedBooks,
                role
            );
        }

        updateIssuedPagination();


        // ======================================
        // STUDENT ISSUED BOOK COUNT
        // ======================================

        if (role !== "admin") {
            const countElement =
                document.getElementById(
                    "myIssuedBooksCount"
                );

            if (countElement) {
                countElement.innerText =
                    issuedBooks.length;
            }
        }

    } catch (error) {
        console.error(
            "Issued books error:",
            error
        );

        table.innerHTML = `
            <tr>
                <td
                    colspan="${role === "admin" ? 8 : 6}"
                    class="text-center text-danger">
                    Failed to load issued books.
                </td>
            </tr>
        `;

        const pagination =
            document.getElementById(
                "issuedPagination"
            );

        if (pagination) {
            pagination.innerHTML = "";
        }
    }
}


// ======================================
// RENDER ISSUED BOOKS
// ======================================

function renderIssuedBooks(books, role) {
    const table =
        document.getElementById("issuedBookTable");

    if (!table) return;

    table.innerHTML = "";

    if (books.length === 0) {
        table.innerHTML = `
            <tr>
                <td
                    colspan="${role === "admin" ? 8 : 6}"
                    class="text-center text-muted">
                    No matching issued books found.
                </td>
            </tr>
        `;
        return;
    }

    books.forEach(book => {
        const issueDate =
            book.issue_date
                ? new Date(
                    book.issue_date
                ).toLocaleDateString()
                : "-";

        const dueDate =
            book.due_date
                ? new Date(
                    book.due_date
                ).toLocaleDateString()
                : "-";

        const fine =
            Number(book.fine || 0);

        if (role === "admin") {
            table.innerHTML += `
                <tr>
                    <td>${book.book_title || "-"}</td>
                    <td>${book.author || "-"}</td>
                    <td>${book.student_name || "-"}</td>
                    <td>${issueDate}</td>
                    <td>${dueDate}</td>
                    <td>₹${fine}</td>
                    <td>
                        <span class="badge bg-primary">
                            Issued
                        </span>
                    </td>
                    <td>
                        <button
                            class="btn btn-success btn-sm"
                            onclick="returnBook(${book.id})">
                            Return
                        </button>
                    </td>
                </tr>
            `;
        } else {
            table.innerHTML += `
                <tr>
                    <td>${book.book_title || "-"}</td>
                    <td>${book.author || "-"}</td>
                    <td>${issueDate}</td>
                    <td>${dueDate}</td>
                    <td>₹${fine}</td>
                    <td>
                        <span class="badge bg-primary">
                            Issued
                        </span>
                    </td>
                </tr>
            `;
        }
    });
}


// ======================================
// ISSUED BOOK PAGINATION
// ======================================

function updateIssuedPagination() {
    const pagination =
        document.getElementById(
            "issuedPagination"
        );

    if (!pagination) return;

    if (issuedTotalPages <= 1) {
        pagination.innerHTML = "";
        return;
    }

    pagination.innerHTML = `
        <button
            class="btn btn-outline-primary me-2"
            onclick="loadMyIssuedBooks(${issuedCurrentPage - 1})"
            ${issuedCurrentPage <= 1 ? "disabled" : ""}>
            ← Previous
        </button>

        <span class="fw-bold mx-2">
            Page ${issuedCurrentPage}
            of ${issuedTotalPages}
        </span>

        <button
            class="btn btn-outline-primary ms-2"
            onclick="loadMyIssuedBooks(${issuedCurrentPage + 1})"
            ${issuedCurrentPage >= issuedTotalPages ? "disabled" : ""}>
            Next →
        </button>
    `;
}


// ======================================
// SEARCH ISSUED BOOKS
// ======================================

function searchIssuedBooks() {
    const searchInput =
        document.getElementById(
            "issuedBookSearch"
        );

    const table =
        document.getElementById(
            "issuedBookTable"
        );

    if (!searchInput || !table) return;

    const keyword =
        searchInput.value
            .toLowerCase()
            .trim();

    const role =
        localStorage.getItem("role");

    // Empty search -> restore pagination
    if (keyword === "") {
        loadMyIssuedBooks(1);
        return;
    }

    const filteredBooks =
        issuedBooksData.filter(book =>
            (book.book_title || "")
                .toLowerCase()
                .includes(keyword) ||

            (book.author || "")
                .toLowerCase()
                .includes(keyword) ||

            (book.student_name || "")
                .toLowerCase()
                .includes(keyword) ||

            (book.status || "")
                .toLowerCase()
                .includes(keyword)
        );

    renderIssuedBooks(
        filteredBooks,
        role
    );

    const pagination =
        document.getElementById(
            "issuedPagination"
        );

    if (pagination) {
        pagination.innerHTML = "";
    }
}


// ======================================
// RETURN BOOK - ADMIN ONLY
// ======================================

async function returnBook(issuedBookId) {
    const confirmReturn = confirm(
        "Are you sure you want to return this book?"
    );

    if (!confirmReturn) return;

    const token =
        localStorage.getItem("token");

    try {
        const response = await fetch(
            API + "/return-book/" + issuedBookId,
            {
                method: "PUT",

                headers: {
                    Authorization:
                        "Bearer " + token
                }
            }
        );

        let data = {};

        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (!response.ok) {
            showToast(data.detail || "Failed to return book.", "error");
            return;
        }

        showToast("Book returned successfully!", "success");

        await loadMyIssuedBooks(1);

        if (typeof loadStats === "function") {
            await loadStats();
        }

        if (typeof loadBooks === "function") {
            await loadBooks(currentPage);
        }

    } catch (error) {
        console.error(
            "Return book error:",
            error
        );

        showToast("Something went wrong while returning the book.", "error");
    }
}


// ======================================
// ROLE BASED UI
// ======================================

function applyRoleBasedUI() {
    const role =
        localStorage.getItem("role");

    const addBookBtn =
        document.getElementById(
            "addBookBtn"
        );

    const issueBookBtn =
        document.getElementById(
            "issueBookBtn"
        );

    if (role === "admin") {
        if (addBookBtn) {
            addBookBtn.style.display = "block";
        }

        if (issueBookBtn) {
            issueBookBtn.style.display = "block";
        }

    } else {
        if (addBookBtn) {
            addBookBtn.style.display = "none";
        }

        if (issueBookBtn) {
            issueBookBtn.style.display = "none";
        }
    }
}


// ======================================
// LOAD ISSUE BOOK DATA - ADMIN
// ======================================

window.loadIssueBookData = async function () {
    const token =
        localStorage.getItem("token");

    const role =
        localStorage.getItem("role");

    if (role !== "admin") return;

    const studentSelect =
        document.getElementById(
            "issueStudent"
        );

    const bookSelect =
        document.getElementById(
            "issueBook"
        );

    if (!studentSelect || !bookSelect) return;

    try {
        // ======================================
        // LOAD STUDENTS
        // ======================================

        const usersResponse =
            await fetch(
                API + "/students",
                {
                    headers: {
                        Authorization:
                            "Bearer " + token
                    }
                }
            );

        if (usersResponse.ok) {
            const users =
                await usersResponse.json();

            studentSelect.innerHTML = `
                <option value="">
                    Select Student
                </option>
            `;

            users.forEach(user => {
                studentSelect.innerHTML += `
                    <option value="${user.id}">
                        ${user.name || user.username || "Student"}
                        - ${user.email}
                    </option>
                `;
            });
        }


        // ======================================
        // LOAD BOOKS
        // ======================================

        const booksResponse =
            await fetch(
                API + "/books?page=1&page_size=100",
                {
                    headers: {
                        Authorization:
                            "Bearer " + token
                    }
                }
            );

        if (booksResponse.ok) {
            const data =
                await booksResponse.json();

            const books =
                data.books || data;

            bookSelect.innerHTML = `
                <option value="">
                    Select Book
                </option>
            `;

            books.forEach(book => {
                bookSelect.innerHTML += `
                    <option value="${book.id}">
                        ${book.title}
                        - ${book.author}
                    </option>
                `;
            });
        }

    } catch (error) {
        console.error(
            "Load issue book data error:",
            error
        );
    }
};


// ======================================
// ADMIN ISSUE BOOK
// ======================================

async function adminIssueBook() {

    const token =
        localStorage.getItem("token");

    const studentId =
        document.getElementById(
            "issueStudent"
        )?.value;

    const bookId =
        document.getElementById(
            "issueBook"
        )?.value;

    const dueDate =
        document.getElementById(
            "issueDueDate"
        )?.value;


    // ======================================
    // VALIDATION
    // ======================================

    if (!studentId) {
        showToast(
            "Please select a student.",
            "warning"
        );
        return;
    }

    if (!bookId) {
        showToast(
            "Please select a book.",
            "warning"
        );
        return;
    }

    if (!dueDate) {
        showToast(
            "Please select a due date.",
            "warning"
        );
        return;
    }


    const dueDateTime =
        dueDate + "T23:59:59";


    try {

        const response = await fetch(
            API + "/issue-book",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",

                    Authorization:
                        "Bearer " + token
                },

                body: JSON.stringify({
                    book_id: parseInt(bookId),
                    user_id: parseInt(studentId),
                    due_date: dueDateTime
                })
            }
        );


        // ======================================
        // HANDLE API ERROR
        // ======================================

        if (!response.ok) {

            let errorMessage =
                "Unable to issue book.";

            try {

                const errorData =
                    await response.json();

                errorMessage =
                    errorData.detail ||
                    errorMessage;

            } catch {

                // Ignore JSON parsing error

            }

            showToast(
                errorMessage,
                "error"
            );

            return;
        }


        // ======================================
        // SUCCESS
        // ======================================

        showToast(
            "Book issued successfully!",
            "success"
        );


        // ======================================
        // CLOSE MODAL
        // ======================================

        const modalElement =
            document.getElementById(
                "issueBookModal"
            );

        const modal =
            bootstrap.Modal.getInstance(
                modalElement
            );

        if (modal) {
            modal.hide();
        }


        // ======================================
        // RESET FORM
        // ======================================

        document.getElementById(
            "issueStudent"
        ).value = "";

        document.getElementById(
            "issueBook"
        ).value = "";

        document.getElementById(
            "issueDueDate"
        ).value = "";


        // ======================================
        // REFRESH DATA
        // ======================================

        await loadMyIssuedBooks(1);

        if (typeof loadStats === "function") {
            await loadStats();
        }

    }

    catch (error) {

        console.error(
            "Issue book error:",
            error
        );

        showToast(
            "Something went wrong while issuing the book.",
            "error"
        );

    }

}


// ======================================
// LOAD BOOK RECOMMENDATIONS
// ======================================

async function loadRecommendations() {

    const token =
        localStorage.getItem("token");

    const role =
        localStorage.getItem("role");

    const section =
        document.getElementById(
            "recommendationsSection"
        );

    const container =
        document.getElementById(
            "recommendationsContainer"
        );


    // ======================================
    // STUDENT ONLY
    // ======================================

    if (role !== "student") {

        if (section) {
            section.classList.add("d-none");
        }

        return;
    }


    if (section) {
        section.classList.remove("d-none");
    }


    try {

        container.innerHTML = `
            <div class="text-center text-muted py-4">
                Loading recommendations...
            </div>
        `;


        const response = await fetch(
            API + "/recommendations",
            {
                headers: {
                    Authorization:
                        "Bearer " + token
                }
            }
        );


        if (!response.ok) {

            throw new Error(
                "Failed to load recommendations."
            );

        }


        const data =
            await response.json();


        const recommendations =
            data.recommendations || [];


        // ======================================
        // NO RECOMMENDATIONS
        // ======================================

        if (recommendations.length === 0) {

            container.innerHTML = `
                <div class="col-12">

                    <div class="alert alert-info text-center">

                        📚 No recommendations available yet.
                        Issue some books to get personalized recommendations!

                    </div>

                </div>
            `;

            return;
        }


        // ======================================
        // DISPLAY RECOMMENDATIONS
        // ======================================

        container.innerHTML =
            recommendations.map(
                book => `

                <div class="col-md-6 col-lg-4">

                    <div class="card shadow-sm border-0 h-100">

                        <div class="card-body d-flex flex-column">

                            <div class="d-flex justify-content-between align-items-start mb-2">

                                <span class="fs-3">
                                    📚
                                </span>

                                <span class="badge bg-primary">

                                    ${book.similarity_score}% Match

                                </span>

                            </div>


                            <h5 class="card-title fw-bold">

                                ${book.title}

                            </h5>


                            <p class="text-muted mb-2">

                                ✍️ ${book.author}

                            </p>


                            <div class="mt-auto">

                                <span class="badge bg-secondary me-2">

                                    ${book.genre || "General"}

                                </span>


                                <span class="text-success fw-bold">

                                    ₹${book.price || "N/A"}

                                </span>

                            </div>

                        </div>

                    </div>

                </div>

            `
            ).join("");

    }

    catch (error) {

        console.error(
            "Recommendation error:",
            error
        );

        container.innerHTML = `
            <div class="col-12">

                <div class="alert alert-danger text-center">

                    Failed to load recommendations.

                </div>

            </div>
        `;

    }

}



// ======================================
// INITIALIZE DASHBOARD
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    () => {
        const token =
            localStorage.getItem("token");

        if (!token) return;

        applyRoleBasedUI();

        if (
            document.getElementById("bookTable")
        ) {
            loadBooks(1);
        }

        if (
            document.getElementById(
                "issuedBookTable"
            )
        ) {
            loadMyIssuedBooks(1);
        }

        if (
            localStorage.getItem("role") === "admin"
        ) {
            if (
                document.getElementById(
                    "issueStudent"
                ) &&
                document.getElementById(
                    "issueBook"
                )
            ) {
                window.loadIssueBookData();
            }
        }
    }
);

// ======================================
// DASHBOARD STATISTICS
// ======================================

async function loadStats() {
    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    // Stats are only for admin
    if (role !== "admin") {
        return;
    }

    try {
        const response = await fetch(API + "/stats", {
            headers: {
                Authorization: "Bearer " + token
            }
        });

        if (!response.ok) {
            throw new Error("Failed to load dashboard statistics");
        }

        const data = await response.json();

        const totalBooks = document.getElementById("totalBooks");
        const totalUsers = document.getElementById("totalUsers");
        const totalContacts = document.getElementById("totalContacts");

        if (totalBooks) {
            totalBooks.innerText = data.total_books;
        }

        if (totalUsers) {
            totalUsers.innerText = data.total_users;
        }

        if (totalContacts) {
            totalContacts.innerText = data.total_contacts;
        }

    } catch (error) {
        console.error("Stats error:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {

    const token = localStorage.getItem("token");

    if (!token) {
        return;
    }

    applyRoleBasedUI();

    // Load dashboard cards
    loadStats();

    if (document.getElementById("bookTable")) {
        loadBooks(1);
    }

    if (document.getElementById("issuedBookTable")) {
        loadMyIssuedBooks(1);
    }

    if (
        localStorage.getItem("role") === "admin" &&
        document.getElementById("issueStudent") &&
        document.getElementById("issueBook")
    ) {
        window.loadIssueBookData();
    }
});

// ======================================
// TOTAL BOOKS CARD
// ======================================

function openBooksCard() {

    const booksSection =
        document.getElementById("booksSection");

    if (booksSection) {

        booksSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

}



// ======================================
// TOTAL USERS CARD
// ======================================

async function openUsersCard() {

    const token =
        localStorage.getItem("token");

    const table =
        document.getElementById(
            "usersModalTable"
        );

    try {

        table.innerHTML = `
            <tr>
                <td
                    colspan="4"
                    class="text-center"
                >
                    Loading users...
                </td>
            </tr>
        `;


        const response =
            await fetch(
                API + "/users",
                {
                    headers: {
                        Authorization:
                            "Bearer " + token
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load users"
            );

        }


        const users =
            await response.json();


        table.innerHTML = "";


        if (users.length === 0) {

            table.innerHTML = `
                <tr>
                    <td
                        colspan="4"
                        class="text-center"
                    >
                        No users found.
                    </td>
                </tr>
            `;

        }

        else {

            users.forEach(user => {

                table.innerHTML += `

                    <tr>

                        <td>
                            ${user.id}
                        </td>

                        <td>
                            ${user.username}
                        </td>

                        <td>
                            ${user.email}
                        </td>

                        <td>
                            <span class="badge bg-primary">
                                ${user.role}
                            </span>
                        </td>

                    </tr>

                `;

            });

        }


        const modal =
            new bootstrap.Modal(
                document.getElementById(
                    "usersModal"
                )
            );


        modal.show();

    }

    catch (error) {

        console.error(
            "Users error:",
            error
        );

        showToast(
            "Failed to load users.",
            "error"
        );

    }

}



// ======================================
// CONTACT MESSAGES CARD
// ======================================

async function openContactsCard() {

    const token =
        localStorage.getItem("token");

    const table =
        document.getElementById(
            "contactsModalTable"
        );

    try {

        table.innerHTML = `
            <tr>
                <td
                    colspan="5"
                    class="text-center"
                >
                    Loading messages...
                </td>
            </tr>
        `;


        const response =
            await fetch(
                API + "/contacts",
                {
                    headers: {
                        Authorization:
                            "Bearer " + token
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load messages"
            );

        }


        const contacts =
            await response.json();


        table.innerHTML = "";


        if (contacts.length === 0) {

            table.innerHTML = `
                <tr>
                    <td
                        colspan="5"
                        class="text-center"
                    >
                        No contact messages found.
                    </td>
                </tr>
            `;

        }

        else {

            contacts.forEach(contact => {

                table.innerHTML += `

                    <tr>

                        <td>
                            ${contact.id}
                        </td>

                        <td>
                            ${contact.name}
                        </td>

                        <td>
                            ${contact.email}
                        </td>

                        <td>
                            ${contact.subject}
                        </td>

                        <td>
                            ${contact.message}
                        </td>

                    </tr>

                `;

            });

        }


        const modal =
            new bootstrap.Modal(
                document.getElementById(
                    "contactsModal"
                )
            );


        modal.show();

    }

    catch (error) {

        console.error(
            "Contacts error:",
            error
        );

        showToast(
            "Failed to load contact messages.",
            "error"
        );

    }

}