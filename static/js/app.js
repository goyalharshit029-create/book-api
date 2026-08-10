const API = "";

let issuedBooksData = [];
let currentPage = 1;
let pageSize = 10;
let totalPages = 1;

// ---------- AUTH CHECK ----------
function checkAuth() {

    if (window.location.pathname === "/dashboard") {

        const token = localStorage.getItem("token");

        if (!token) {

            alert("Please login first.");

            window.location = "/login-page";

        }

    }

}

checkAuth();


// ---------- REGISTER ----------
async function registerUser() {

    const username = document.getElementById("username").value.trim();

    const email = document.getElementById("email").value.trim();

    const password = document.getElementById("password").value.trim();

    if (!username || !email || !password) {

        alert("Please fill all fields.");

        return;

    }

    const response = await fetch(API + "/register", {

        method: "POST",

        headers: {

            "Content-Type": "application/json"

        },

        body: JSON.stringify({

            username: username,

            email: email,

            password: password

        })

    });

    const data = await response.json();

    if (response.ok) {

        alert("Registration Successful!");

        window.location = "/login-page";

    }

    else {

        alert(data.detail || "Registration Failed");

    }

}
// ---------- LOGIN ----------
async function loginUser() {

    const email = document.getElementById("email").value.trim();

    const password = document.getElementById("password").value.trim();

    if (!email || !password) {

        alert("Please enter Email and Password.");

        return;

    }

    const form = new URLSearchParams();

    form.append("username", email);

    form.append("password", password);

    const response = await fetch(API + "/login", {

        method: "POST",

        headers: {

            "Content-Type":
                "application/x-www-form-urlencoded"

        },

        body: form

    });

    const data = await response.json();

    if (response.ok) {

        localStorage.setItem("token", data.access_token);
        localStorage.setItem("role", data.role);

        alert("Login Successful!");

        window.location = "/dashboard";

    }

    else {

        alert(data.detail || "Invalid Credentials");

    }

}



// ---------- LOGOUT ----------
function logout() {

    localStorage.removeItem("token");
    localStorage.removeItem("role");

    window.location = "/login-page";

}
// ---------- LOAD BOOKS ----------
async function loadBooks(page = 1) {

    const table = document.getElementById("bookTable");

    if (!table) return;

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    const response = await fetch(
        API + "/books?page=" + page + "&page_size=" + pageSize,
        {
            headers: {
                Authorization: "Bearer " + token
            }
        }
    );

    if (!response.ok) {

        alert("Unable to load books.");

        return;
    }

    const data = await response.json();

    currentPage = data.page;
    totalPages = data.total_pages;

    const books = data.books;

    // Change table heading according to role
    const head = document.getElementById("bookTableHead");

    if (head) {

        if (role === "admin") {

            head.innerHTML = `
                <tr>
                    <th>ID</th>
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
                    <th>ID</th>
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

    books.forEach(book => {

        // ADMIN
        if (role === "admin") {

            table.innerHTML += `
                <tr>

                    <td>${book.id}</td>

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

        }

        // STUDENT
        else {

            table.innerHTML += `
                <tr>

                    <td>${book.id}</td>

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
}
// ---------- PAGINATION ----------
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
// ---------- SEARCH BOOKS ----------
async function searchBooks() {

    const keyword = document
        .getElementById("search")
        .value
        .toLowerCase()
        .trim();

    const table = document.getElementById("bookTable");

    if (!table) return;

    // If search box is empty, load normal paginated books
    if (keyword === "") {
        loadBooks(1);
        return;
    }

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");

    try {

        // Get all books for searching
        const response = await fetch(
            API + "/books?page=1&page_size=100",
            {
                headers: {
                    Authorization: "Bearer " + token
                }
            }
        );

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        const books = data.books;

        const filteredBooks = books.filter(book =>
            book.title.toLowerCase().includes(keyword) ||
            book.author.toLowerCase().includes(keyword) ||
            book.genre.toLowerCase().includes(keyword)
        );

        table.innerHTML = "";

        filteredBooks.forEach(book => {

            let actions = "";

            if (role === "admin") {

                actions = `
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
                `;

            }

            table.innerHTML += `
                <tr>

                    <td>${book.id}</td>

                    <td>${book.title}</td>

                    <td>${book.author}</td>

                    <td>${book.genre}</td>

                    <td>₹${book.price}</td>

                    <td>${book.published_year}</td>

                    <td>
                        ${actions}
                    </td>

                </tr>
            `;

        });

        // Hide pagination while searching
        document.getElementById("pagination").innerHTML = "";

    }
    catch (error) {

        console.log("Search error:", error);

    }
}
// ---------- UPDATE BOOK ----------
async function addBook() {

    const title = document.getElementById("title").value.trim();
    const author = document.getElementById("author").value.trim();
    const genre = document.getElementById("genre").value.trim();
    const price = parseFloat(document.getElementById("price").value);
    const published_year = parseInt(document.getElementById("year").value);

    if (
        !title ||
        !author ||
        !genre ||
        isNaN(price) ||
        isNaN(published_year)
    ) {

        alert("Please fill all fields.");
        return;

    }

    const token = localStorage.getItem("token");

    const response = await fetch(

        window.currentBookId
            ? API + "/books/" + window.currentBookId
            : API + "/books",

        {

            method: window.currentBookId ? "PUT" : "POST",

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

        alert(

            window.currentBookId
                ? "Book Updated Successfully!"
                : "Book Added Successfully!"

        );

        document.getElementById("title").value = "";
        document.getElementById("author").value = "";
        document.getElementById("genre").value = "";
        document.getElementById("price").value = "";
        document.getElementById("year").value = "";

        window.currentBookId = null;
        document.querySelector("#addBookModal .btn-success").innerText = "Save Book";

        loadBooks();

        const modal = bootstrap.Modal.getInstance(
            document.getElementById("addBookModal")
        );

        if (modal) {

            modal.hide();

        }

    }

    else {

        alert(data.detail || "Operation Failed.");

    }

}
// ---------- DELETE BOOK ----------
async function deleteBook(id) {

    const ok = confirm("Are you sure you want to delete this book?");

    if (!ok) return;

    const token = localStorage.getItem("token");

    const response = await fetch(API + "/books/" + id, {

        method: "DELETE",

        headers: {
            Authorization: "Bearer " + token
        }

    });

    if (response.ok) {

        alert("Book Deleted Successfully!");

        loadBooks();

    } else {

        const data = await response.json();

        alert(data.detail || "Delete Failed");

    }

}


// ---------- EDIT BOOK ----------
async function editBook(id) {

    const token = localStorage.getItem("token");

    const response = await fetch(API + "/books/" + id, {

        headers: {
            Authorization: "Bearer " + token
        }

    });

    if (!response.ok) {

        alert("Unable to fetch book details.");

        return;

    }

    const book = await response.json();

    document.getElementById("title").value = book.title;

    document.getElementById("author").value = book.author;

    document.getElementById("genre").value = book.genre;

    document.getElementById("price").value = book.price;

    document.getElementById("year").value = book.published_year;

    // Save current editing id
    window.currentBookId = id;

    document.querySelector("#addBookModal .btn-success").innerText = "Update Book";

    const modal = new bootstrap.Modal(
        document.getElementById("addBookModal")
    );

    modal.show();

}
// ---------- CONTACT ----------
async function sendContact() {

    const name = document.getElementById("contactName").value.trim();
    const email = document.getElementById("contactEmail").value.trim();
    const subject = document.getElementById("contactSubject").value.trim();
    const message = document.getElementById("contactMessage").value.trim();

    if (!name || !email || !subject || !message) {
        alert("Please fill all fields.");
        return;
    }

    const response = await fetch(API + "/contact", {

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

    });

    const data = await response.json();

    if (response.ok) {

        alert("Message Sent Successfully!");

        document.getElementById("contactName").value = "";
        document.getElementById("contactEmail").value = "";
        document.getElementById("contactSubject").value = "";
        document.getElementById("contactMessage").value = "";

        // Refresh dashboard stats if dashboard is open
        if (typeof loadStats === "function") {
            loadStats();
        }

    } else {

        alert(data.detail || "Failed to send message.");

    }

}


// ---------- LOAD ISSUED BOOKS ----------
async function loadMyIssuedBooks() {

    const table = document.getElementById("issuedBookTable");

    if (!table) return;

    const token = localStorage.getItem("token");
    const role = localStorage.getItem("role");
    const totalBooksCard = document.getElementById("totalBooksCard");
    const totalUsersCard = document.getElementById("totalUsersCard");
    const totalContactsCard = document.getElementById("totalContactsCard");
    const myIssuedBooksCard = document.getElementById("myIssuedBooksCard");

    if (role === "admin") {

        totalBooksCard.classList.remove("d-none");
        totalUsersCard.classList.remove("d-none");
        totalContactsCard.classList.remove("d-none");

        myIssuedBooksCard.classList.add("d-none");

    } else {

        totalBooksCard.classList.add("d-none");
        totalUsersCard.classList.add("d-none");
        totalContactsCard.classList.add("d-none");

        myIssuedBooksCard.classList.remove("d-none");

    }

    // Get table header
    const head = document.getElementById("issuedBookHead");

    // Change table columns according to role
    if (head) {

        if (role === "admin") {

            head.innerHTML = `
                <tr>
                    <th>Issue ID</th>
                    <th>Book</th>
                    <th>Author</th>
                    <th>Student</th>
                    <th>Issue Date</th>
                    <th>Due Date</th>
                    <th>Return Date</th>
                    <th>Fine</th>
                    <th>Status</th>
                </tr>
            `;

        } else {

            head.innerHTML = `
                <tr>
                    <th>Book</th>
                    <th>Author</th>
                    <th>Issue Date</th>
                    <th>Due Date</th>
                    <th>Return Date</th>
                    <th>Fine</th>
                    <th>Status</th>
                </tr>
            `;

        }
    }

    let endpoint = "";

    // Admin sees all issued books
    if (role === "admin") {

        endpoint = API + "/issued-books";

    } else {

        // Student sees only their own books
        endpoint = API + "/my-issued-books";

    }

    const response = await fetch(
        endpoint,
        {
            headers: {
                Authorization: "Bearer " + token
            }
        }
    );

    if (!response.ok) {

        console.log("Unable to load issued books.");

        return;
    }

    const books = await response.json();
    issuedBooksData = books;
    // Update student issued books count
    const countElement = document.getElementById("myIssuedBooksCount");

    if (countElement) {
        countElement.innerText = books.length;
    }

    table.innerHTML = "";

    books.forEach(book => {

        const returnDate = book.return_date
            ? new Date(book.return_date).toLocaleDateString()
            : "Not Returned";

        const issueDate = new Date(
            book.issue_date
        ).toLocaleDateString();

        const dueDate = new Date(
            book.due_date
        ).toLocaleDateString();


        // ==========================
        // ADMIN VIEW
        // ==========================

        if (role === "admin") {

            table.innerHTML += `
                <tr>

                    <td>${book.id}</td>

                    <td>${book.book_title}</td>

                    <td>${book.author}</td>

                    <td>${book.student_name}</td>

                    <td>${issueDate}</td>

                    <td>${dueDate}</td>

                    <td>${returnDate}</td>

                    <td>₹${book.fine}</td>

                    <td>
                        <span class="badge ${book.status === "issued"
                    ? "bg-primary"
                    : "bg-success"
                }">
                            ${book.status}
                        </span>
                    </td>

                </tr>
            `;

        }

        // ==========================
        // STUDENT VIEW
        // ==========================

        else {

            table.innerHTML += `
                <tr>

                    <td>${book.book_title}</td>

                    <td>${book.author}</td>

                    <td>${issueDate}</td>

                    <td>${dueDate}</td>

                    <td>${returnDate}</td>

                    <td>₹${book.fine}</td>

                    <td>
                        <span class="badge ${book.status === "issued"
                    ? "bg-primary"
                    : "bg-success"
                }">
                            ${book.status === "issued" ? "Issued" : "Returned"}
                        </span>
                    </td>

                </tr>
            `;

        }

    });

}

// ---------- SEARCH ISSUED BOOKS ----------
function searchIssuedBooks() {

    const keyword = document
        .getElementById("issuedBookSearch")
        .value
        .toLowerCase()
        .trim();

    const table = document.getElementById("issuedBookTable");

    if (!table) return;

    const filteredBooks = issuedBooksData.filter(book =>

        book.book_title.toLowerCase().includes(keyword) ||

        book.author.toLowerCase().includes(keyword) ||

        (book.student_name &&
            book.student_name.toLowerCase().includes(keyword)) ||

        book.status.toLowerCase().includes(keyword)

    );

    table.innerHTML = "";

    filteredBooks.forEach(book => {

        const returnDate = book.return_date
            ? new Date(book.return_date).toLocaleDateString()
            : "Not Returned";

        const issueDate = new Date(
            book.issue_date
        ).toLocaleDateString();

        const dueDate = new Date(
            book.due_date
        ).toLocaleDateString();

        table.innerHTML += `
            <tr>

                <td>${book.book_title}</td>

                <td>${book.author}</td>

                ${localStorage.getItem("role") === "admin"
                ? `<td>${book.student_name}</td>`
                : ""
            }

                <td>${issueDate}</td>

                <td>${dueDate}</td>

                <td>${returnDate}</td>

                <td>₹${book.fine}</td>

                <td>

                    <span class="badge ${book.status === "issued"
                ? "bg-primary"
                : "bg-success"
            }">

                        ${book.status === "issued"
                ? "Issued"
                : "Returned"
            }

                    </span>

                </td>

            </tr>
        `;

    });
}


function applyRoleBasedUI() {

    const role = localStorage.getItem("role");

    const addBookBtn = document.getElementById("addBookBtn");

    if (!addBookBtn) return;

    if (role === "admin") {

        addBookBtn.style.display = "block";

    } else {

        addBookBtn.style.display = "none";

    }
}