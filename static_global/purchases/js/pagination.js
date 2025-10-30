document.addEventListener("DOMContentLoaded", function () {
  const rowsPerPage = 5;
  const table = document.getElementById("supplierTable");
  const rows = table.querySelectorAll("tr");
  const pagination = document.getElementById("pagination");
  const totalPages = Math.ceil(rows.length / rowsPerPage);

  function showPage(page) {
    const start = (page - 1) * rowsPerPage;
    const end = start + rowsPerPage;

    rows.forEach((row, index) => {
      row.style.display = (index >= start && index < end) ? "" : "none";
    });

    updatePagination(page);
  }

  function updatePagination(activePage) {
    pagination.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement("li");
      li.className = `page-item ${i === activePage ? "active" : ""}`;
      li.innerHTML = `<button class="page-link">${i}</button>`;
      li.addEventListener("click", () => showPage(i));
      pagination.appendChild(li);
    }
  }

  // Initial display
  showPage(1);
});

document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("searchInput");
  const cityFilter = document.getElementById("cityFilter");
  const tableRows = document.querySelectorAll("#supplierTable tr");

  function filterTable() {
    const searchValue = searchInput.value.toLowerCase();
    const selectedCity = cityFilter.value.toLowerCase();

    tableRows.forEach(row => {
      const cells = Array.from(row.getElementsByTagName("td"));
      const rowText = cells.map(cell => cell.textContent.toLowerCase()).join(" ");
      const cityText = cells[5]?.textContent.toLowerCase() || "";

      const matchesSearch = rowText.includes(searchValue);
      const matchesCity = selectedCity === "" || cityText.includes(selectedCity);

      row.style.display = (matchesSearch && matchesCity) ? "" : "none";
    });
  }

  searchInput.addEventListener("input", filterTable);
  cityFilter.addEventListener("change", filterTable);
});
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const cityFilter = document.getElementById("cityFilter");
  const supplierTable = document.getElementById("supplierTable");

  function normalize(str) {
    return str.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function filterTable() {
    const searchValue = normalize(searchInput.value.trim());
    const selectedCity = normalize(cityFilter.value.trim());

    const rows = supplierTable.querySelectorAll("tr");

    rows.forEach(row => {
      const cells = row.querySelectorAll("td");
      if (cells.length === 0) return;

      const rowText = Array.from(cells)
        .map(cell => normalize(cell.innerText))
        .join(" ");

      const cityText = normalize(cells[5]?.innerText || "");

      const matchSearch = rowText.includes(searchValue);
      const matchCity = selectedCity === "" || cityText.includes(selectedCity);

      if (matchSearch && matchCity) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

  searchInput.addEventListener("input", filterTable);
  cityFilter.addEventListener("change", filterTable);
});

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  const cityFilter = document.getElementById('cityFilter');
  const countryFilter = document.getElementById('countryFilter');
  const tableRows = document.querySelectorAll('#supplierTable tr');

  function filterSuppliers() {
    const searchValue = searchInput.value.toLowerCase();
    const selectedCity = cityFilter.value;
    const selectedCountry = countryFilter.value;

    tableRows.forEach(row => {
      const name = row.cells[1].textContent.toLowerCase();
      const email = row.cells[2].textContent.toLowerCase();
      const city = row.cells[5].textContent.trim();
      const country = row.cells[4].textContent.trim();

      const matchesSearch = name.includes(searchValue) || email.includes(searchValue);
      const matchesCity = !selectedCity || city === selectedCity;
      const matchesCountry = !selectedCountry || country.includes(selectedCountry);

      if (matchesSearch && matchesCity && matchesCountry) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }

  searchInput.addEventListener('input', filterSuppliers);
  cityFilter.addEventListener('change', filterSuppliers);
  countryFilter.addEventListener('change', filterSuppliers);
});

