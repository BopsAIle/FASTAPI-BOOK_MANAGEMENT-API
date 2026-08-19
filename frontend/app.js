const TOKEN_KEY = "access_token";

const api = {
  books: "/books",
  authors: "/authors",
  categories: "/categories",
  login: "/auth/login",
  register: "/auth/register",
  me: "/auth/me",
};

const dom = {
  authScreen: document.getElementById("auth-screen"),
  appShell: document.getElementById("app-shell"),
  loginForm: document.getElementById("login-form"),
  registerForm: document.getElementById("register-form"),
  loginMessage: document.getElementById("login-message"),
  registerMessage: document.getElementById("register-message"),
  tabLogin: document.getElementById("tab-login"),
  tabRegister: document.getElementById("tab-register"),
  currentUserEmail: document.getElementById("current-user-email"),
  logoutButton: document.getElementById("btn-logout"),
  pages: document.querySelectorAll(".page"),
  navButtons: document.querySelectorAll(".app-nav button"),
  bookList: document.getElementById("book-list"),
  authorList: document.getElementById("author-list"),
  categoryList: document.getElementById("category-list"),
  bookForm: document.getElementById("book-form"),
  authorForm: document.getElementById("author-form"),
  categoryForm: document.getElementById("category-form"),
  bookMessage: document.getElementById("book-message"),
  authorMessage: document.getElementById("author-message"),
  categoryMessage: document.getElementById("category-message"),
  authorFilter: document.getElementById("book-author-filter"),
  categoryFilter: document.getElementById("book-category-filter"),
  bookKeyword: document.getElementById("book-keyword"),
  bookYear: document.getElementById("book-year"),
  refreshBooks: document.getElementById("btn-refresh-books"),
};

let authors = [];
let categories = [];
let books = [];
let currentUser = null;

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function showAuth() {
  currentUser = null;
  if (dom.currentUserEmail) dom.currentUserEmail.textContent = "";
  dom.authScreen.hidden = false;
  dom.appShell.hidden = true;
}

function showApp(user) {
  currentUser = user;
  if (dom.currentUserEmail) {
    dom.currentUserEmail.textContent = user.full_name
      ? `${user.full_name} (${user.email})`
      : user.email;
  }
  dom.authScreen.hidden = true;
  dom.appShell.hidden = false;
}

function logout() {
  clearToken();
  authors = [];
  categories = [];
  books = [];
  showAuth();
}

function activatePage(pageId) {
  dom.pages.forEach((page) => page.classList.toggle("active", page.id === pageId));
  dom.navButtons.forEach((btn) => btn.classList.toggle("active", btn.dataset.page === pageId));
}

function isAuthUrl(url) {
  return url.startsWith(api.login) || url.startsWith(api.register);
}

async function fetchJson(url, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401 && !isAuthUrl(url)) {
    logout();
    throw new Error("Phiên đăng nhập hết hạn");
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const detail = error.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join("; ")
      : detail || response.statusText;
    throw new Error(message);
  }
  if (response.status === 204) return null;
  return response.json();
}

function setAuthTab(mode) {
  const isLogin = mode === "login";
  dom.tabLogin.classList.toggle("active", isLogin);
  dom.tabRegister.classList.toggle("active", !isLogin);
  dom.loginForm.hidden = !isLogin;
  dom.registerForm.hidden = isLogin;
  dom.loginMessage.textContent = "";
  dom.registerMessage.textContent = "";
  dom.loginMessage.classList.remove("error");
  dom.registerMessage.classList.remove("error");
}

async function loadAuthors() {
  authors = await fetchJson(api.authors);
  renderAuthors();
  renderAuthorOptions();
}

async function loadCategories() {
  categories = await fetchJson(api.categories);
  renderCategories();
  renderCategoryOptions();
}

async function loadBooks() {
  const params = new URLSearchParams();
  const keyword = dom.bookKeyword.value.trim();
  const year = dom.bookYear.value;
  const authorId = dom.authorFilter.value;
  const categoryId = dom.categoryFilter.value;
  if (keyword) params.append("keyword", keyword);
  if (year) params.append("year", year);
  if (authorId) params.append("author_id", authorId);
  if (categoryId) params.append("category_id", categoryId);
  const query = params.toString();
  books = await fetchJson(`${api.books}${query ? `?${query}` : ""}`);
  renderBooks();
}

function renderAuthorOptions() {
  const authorSelects = document.querySelectorAll("select[name='author_id']");
  const authorFilter = dom.authorFilter;
  authorFilter.innerHTML = "<option value=''>Tất cả tác giả</option>";
  authorSelects.forEach((select) => {
    select.innerHTML = authors.map((author) => `<option value='${author.id}'>${author.name}</option>`).join("");
  });
}

function renderCategoryOptions() {
  const categorySelects = document.querySelectorAll("select[name='category_id']");
  const categoryFilter = dom.categoryFilter;
  categoryFilter.innerHTML = "<option value=''>Tất cả thể loại</option>";
  categorySelects.forEach((select) => {
    select.innerHTML = categories.map((category) => `<option value='${category.id}'>${category.name}</option>`).join("");
  });
}

function formatPrice(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount) || amount <= 0) return "Chưa có giá";
  return `${amount.toLocaleString("vi-VN")} ₫`;
}

function renderBooks() {
  if (books.length === 0) {
    dom.bookList.innerHTML = "<p>Không có sách nào.</p>";
    return;
  }

  dom.bookList.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Ảnh</th>
          <th>Tiêu đề</th>
          <th>Tác giả / Thể loại</th>
          <th>Năm</th>
          <th>Giá</th>
          <th>Hành động</th>
        </tr>
      </thead>
      <tbody>
        ${books.map((book) => `
          <tr>
            <td>${book.cover_image ? `<img src='${book.cover_image}' class='cover-thumb' alt='cover' />` : "-"}</td>
            <td>
              <strong>${book.title}</strong>
              <p>${book.description || "Không có mô tả."}</p>
            </td>
            <td>
              <div>${book.author.name}</div>
              <div>${book.category.name}</div>
            </td>
            <td>${book.published_year}</td>
            <td>${formatPrice(book.price)}</td>
            <td class='actions'>
              <button type="button" class='secondary' onclick='editBook(${JSON.stringify(book.id)})'>Sửa</button>
              <button type="button" class='danger' onclick='deleteBook(${JSON.stringify(book.id)})'>Xóa</button>
              <button type="button" onclick='showCoverUpload(${JSON.stringify(book.id)})'>Upload ảnh</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderAuthors() {
  if (authors.length === 0) {
    dom.authorList.innerHTML = "<p>Chưa có tác giả.</p>";
    return;
  }
  dom.authorList.innerHTML = `
    <table>
      <thead>
        <tr><th>ID</th><th>Tên</th><th>Tiểu sử</th><th>Hành động</th></tr>
      </thead>
      <tbody>
        ${authors.map((author) => `
          <tr>
            <td>${author.id}</td>
            <td>${author.name}</td>
            <td>${author.bio || "-"}</td>
            <td class='actions'>
              <button type="button" class='secondary' onclick='editAuthor(${JSON.stringify(author.id)})'>Sửa</button>
              <button type="button" class='danger' onclick='deleteAuthor(${JSON.stringify(author.id)})'>Xóa</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderCategories() {
  if (categories.length === 0) {
    dom.categoryList.innerHTML = "<p>Chưa có thể loại.</p>";
    return;
  }
  dom.categoryList.innerHTML = `
    <table>
      <thead>
        <tr><th>ID</th><th>Tên</th><th>Mô tả</th><th>Hành động</th></tr>
      </thead>
      <tbody>
        ${categories.map((category) => `
          <tr>
            <td>${category.id}</td>
            <td>${category.name}</td>
            <td>${category.description || "-"}</td>
            <td class='actions'>
              <button type="button" class='secondary' onclick='editCategory(${JSON.stringify(category.id)})'>Sửa</button>
              <button type="button" class='danger' onclick='deleteCategory(${JSON.stringify(category.id)})'>Xóa</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function showCoverUpload(bookId) {
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = "image/png, image/jpeg";
  fileInput.onchange = async () => {
    if (!fileInput.files?.length) return;
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    try {
      await fetchJson(`${api.books}/${bookId}/cover`, {
        method: "POST",
        body: formData,
      });
      await loadBooks();
      alert("Upload thành công.");
    } catch (error) {
      alert(error.message);
    }
  };
  fileInput.click();
}

async function deleteBook(bookId) {
  if (!confirm("Xóa sách này?")) return;
  await fetchJson(`${api.books}/${bookId}`, { method: "DELETE" });
  await loadBooks();
}

async function deleteAuthor(authorId) {
  if (!confirm("Xóa tác giả này? Lưu ý: sẽ không thể xóa nếu có sách liên quan.")) return;
  await fetchJson(`${api.authors}/${authorId}`, { method: "DELETE" });
  await loadAuthors();
  await loadBooks();
}

async function deleteCategory(categoryId) {
  if (!confirm("Xóa thể loại này? Lưu ý: sẽ không thể xóa nếu có sách liên quan.")) return;
  await fetchJson(`${api.categories}/${categoryId}`, { method: "DELETE" });
  await loadCategories();
  await loadBooks();
}

window.editBook = async (bookId) => {
  const book = books.find((item) => item.id === bookId);
  if (!book) return;
  const title = prompt("Tiêu đề", book.title);
  if (title === null) return;
  const published_year = parseInt(prompt("Năm xuất bản", String(book.published_year)) || "", 10);
  if (Number.isNaN(published_year)) return alert("Năm xuất bản không hợp lệ");
  const price = parseInt(prompt("Giá (VND)", String(book.price ?? 0)) || "", 10);
  if (Number.isNaN(price) || price < 0) return alert("Giá sách không hợp lệ");
  const author_id = (prompt("ID tác giả", book.author.id) || "").trim();
  const category_id = (prompt("ID thể loại", book.category.id) || "").trim();
  if (!author_id || !category_id) return;
  const description = prompt("Mô tả", book.description || "");
  await fetchJson(`${api.books}/${bookId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, published_year, price, author_id, category_id, description }),
  });
  await loadBooks();
};

window.editAuthor = async (authorId) => {
  const author = authors.find((item) => item.id === authorId);
  if (!author) return;
  const name = prompt("Tên tác giả", author.name);
  if (name === null) return;
  const bio = prompt("Tiểu sử", author.bio || "");
  await fetchJson(`${api.authors}/${authorId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, bio }),
  });
  await loadAuthors();
  await loadBooks();
};

window.editCategory = async (categoryId) => {
  const category = categories.find((item) => item.id === categoryId);
  if (!category) return;
  const name = prompt("Tên thể loại", category.name);
  if (name === null) return;
  const description = prompt("Mô tả", category.description || "");
  await fetchJson(`${api.categories}/${categoryId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });
  await loadCategories();
  await loadBooks();
};

dom.navButtons.forEach((button) => {
  button.addEventListener("click", () => activatePage(button.dataset.page));
});

dom.bookForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  dom.bookMessage.textContent = "";
  const form = new FormData(dom.bookForm);
  try {
    await fetchJson(api.books, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: form.get("title"),
        description: form.get("description"),
        published_year: Number(form.get("published_year")),
        price: Number(form.get("price")),
        author_id: String(form.get("author_id") || ""),
        category_id: String(form.get("category_id") || ""),
      }),
    });
    dom.bookForm.reset();
    dom.bookMessage.textContent = "Tạo sách thành công.";
    await loadBooks();
  } catch (error) {
    dom.bookMessage.textContent = error.message;
    dom.bookMessage.classList.add("error");
  }
});

dom.authorForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  dom.authorMessage.textContent = "";
  const form = new FormData(dom.authorForm);
  try {
    await fetchJson(api.authors, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: form.get("name"),
        bio: form.get("bio"),
      }),
    });
    dom.authorForm.reset();
    dom.authorMessage.textContent = "Tạo tác giả thành công.";
    await loadAuthors();
  } catch (error) {
    dom.authorMessage.textContent = error.message;
    dom.authorMessage.classList.add("error");
  }
});

dom.categoryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  dom.categoryMessage.textContent = "";
  const form = new FormData(dom.categoryForm);
  try {
    await fetchJson(api.categories, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: form.get("name"),
        description: form.get("description"),
      }),
    });
    dom.categoryForm.reset();
    dom.categoryMessage.textContent = "Tạo thể loại thành công.";
    await loadCategories();
  } catch (error) {
    dom.categoryMessage.textContent = error.message;
    dom.categoryMessage.classList.add("error");
  }
});

dom.refreshBooks.addEventListener("click", loadBooks);

dom.tabLogin.addEventListener("click", () => setAuthTab("login"));
dom.tabRegister.addEventListener("click", () => setAuthTab("register"));
dom.logoutButton.addEventListener("click", logout);

dom.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  dom.loginMessage.textContent = "";
  dom.loginMessage.classList.remove("error");
  const form = new FormData(dom.loginForm);
  try {
    const token = await fetchJson(api.login, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: String(form.get("email") || "").trim(),
        password: String(form.get("password") || ""),
      }),
    });
    setToken(token.access_token);
    await enterApp();
  } catch (error) {
    dom.loginMessage.textContent = error.message;
    dom.loginMessage.classList.add("error");
  }
});

dom.registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  dom.registerMessage.textContent = "";
  dom.registerMessage.classList.remove("error");
  const form = new FormData(dom.registerForm);
  try {
    const token = await fetchJson(api.register, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: String(form.get("email") || "").trim(),
        password: String(form.get("password") || ""),
        full_name: String(form.get("full_name") || "").trim() || null,
      }),
    });
    setToken(token.access_token);
    await enterApp();
  } catch (error) {
    dom.registerMessage.textContent = error.message;
    dom.registerMessage.classList.add("error");
  }
});

async function enterApp() {
  const user = await fetchJson(api.me);
  showApp(user);
  await loadAuthors();
  await loadCategories();
  await loadBooks();
}

async function init() {
  if (!getToken()) {
    showAuth();
    return;
  }
  try {
    await enterApp();
  } catch (error) {
    showAuth();
    if (dom.loginMessage) {
      dom.loginMessage.textContent = error.message;
      dom.loginMessage.classList.add("error");
    }
  }
}

window.addEventListener("DOMContentLoaded", init);
