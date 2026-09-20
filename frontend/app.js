const form = document.getElementById("item-form");
const tableBody = document.getElementById("table-body");



form.addEventListener("submit", async function (e) {e.preventDefault();
  const name = document.getElementById("name").value;
  const price = document.getElementById("price").value;

  try {
    await fetch("/items", {
      headers: {
        "Content-Type": "application/json",
      },

      method: "POST",

      body: JSON.stringify({
        name: name,
        price: Number(price),
      }),
    });

    form.reset();

    await fetchData();
  } catch (err) {
    console.error(err);
  }
});

async function fetchData() {
  try {
    const response = await fetch("/items");
    const data = await response.json();
    const items = data.items;

    tableBody.innerHTML = "";

    items.forEach((item) => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${item.id}</td>
        <td>${item.name}</td>
        <td>${item.price}</td>
        <td>
          <button onclick="handleDelete(${item.id})">
            Delete
          </button>
        </td>
      `;

      tableBody.appendChild(row);
    });
  } catch (err) {
    console.error(err);
  }
}


async function handleDelete(id) {
  try {
    await fetch(`/items/${id}`, {
      headers: {
        "Content-Type": "application/json",
      },

      method: "DELETE",
    });

    await fetchData();
  } catch (err) {
    console.error(err);
  }
}


fetchData();

