document.addEventListener("DOMContentLoaded", function () {
  // Form inputs and buttons
  const planCards = document.querySelectorAll(".plan-card");
  const editTitle = document.getElementById("edit-title");

  const planNameInput = document.getElementById("plan-name");
  const planBadgeInput = document.getElementById("plan-badge");
  const planDescInput = document.getElementById("plan-description");
  const planMonthlyInput = document.getElementById("plan-monthly");
  const planYearlyInput = document.getElementById("plan-yearly");
  const planStatusInput = document.getElementById("plan-status");
  const planOrderInput = document.getElementById("plan-order");
  const statusText = document.getElementById("status-text");
  const featureList = document.getElementById("feature-list");
  const saveBtn = document.querySelector(".btn-save");
  const addFeatureBtn = document.getElementById("add-feature-btn");

  let currentPlanId = null;
  let isCreatingNew = false;

  // Handle "Add New Plan"
  document.getElementById("add-new-plan-btn").addEventListener("click", function () {
    isCreatingNew = true;
    currentPlanId = null;
    editTitle.textContent = "Create New Plan";

    planNameInput.value = "";
    planBadgeInput.value = "";
    planDescInput.value = "";
    planMonthlyInput.value = "";
    planYearlyInput.value = "";
    planStatusInput.checked = true;
    statusText.textContent = "Active";
    planOrderInput.value = "";
    featureList.innerHTML = "";
  });

  // Render features with edit/delete actions
function renderFeatures(features) {
  featureList.innerHTML = "";

  features.forEach((feature) => {
    const div = document.createElement("div");
    div.className = "feature-item";
    div.innerHTML = `
      <div class="feature-info">
        <div class="feature-details">
          <div class="feature-name">${feature.name}</div>
          <div class="feature-value">${feature.value}</div>
        </div>
      </div>
      <div class="feature-actions">
        <button class="btn-action btn-edit">Edit</button>
        <button class="btn-action btn-delete">Delete</button>
      </div>
    `;

    // Add event listeners AFTER inserting into DOM
    featureList.appendChild(div);

    // Edit button → turn display into inputs
    div.querySelector(".btn-edit").addEventListener("click", () => {
      const details = div.querySelector(".feature-details");
      const name = details.querySelector(".feature-name").textContent.trim();
      const value = details.querySelector(".feature-value").textContent.trim();

      details.innerHTML = `
        <input type="text" class="form-control feature-name-input" value="${name}" />
        <input type="text" class="form-control feature-value-input" value="${value}" />
      `;
    });

    // Delete button → remove the feature
    div.querySelector(".btn-delete").addEventListener("click", () => {
      div.remove();
    });
  });
  console.log("Rendering features", features);
}


  // Fill form when editing a plan
  function populateForm(plan) {
    editTitle.textContent = "Edit Plan: " + plan.name;
    planNameInput.value = plan.name;
    planBadgeInput.value = plan.badge || "";
    planDescInput.value = plan.description || "";
    planMonthlyInput.value = plan.price;
    planYearlyInput.value = plan.yearly_price;
    planStatusInput.checked = plan.is_active;
    statusText.textContent = plan.is_active ? "Active" : "Inactive";
    planOrderInput.value = plan.display_order;

    renderFeatures(plan.features || []);
  }

  // Update status label
  planStatusInput.addEventListener("change", () => {
    statusText.textContent = planStatusInput.checked ? "Active" : "Inactive";
  });

  // Load plan details on card click
  planCards.forEach((card) => {
    card.addEventListener("click", () => {
      const planId = card.dataset.id;
      currentPlanId = planId;
      isCreatingNew = false;

      planCards.forEach((c) => c.classList.remove("active"));
      card.classList.add("active");

      fetch(`/api/plans/${planId}/`)
        .then((response) => response.json())
        .then((data) => {
          populateForm(data);
        });
    });
  });

  // Auto-load first active plan
  const firstActiveCard = document.querySelector(".plan-card.active");
  if (firstActiveCard) {
    const firstId = firstActiveCard.dataset.id;
    currentPlanId = firstId;
    fetch(`/api/plans/${firstId}/`)
      .then((response) => response.json())
      .then((data) => {
        populateForm(data);
      });
  }

  // Save changes or create new plan
  saveBtn.addEventListener("click", () => {
    const features = Array.from(document.querySelectorAll(".feature-item")).map(item => {
      const nameInput = item.querySelector(".feature-name-input");
      const valueInput = item.querySelector(".feature-value-input");

      return {
        name: nameInput ? nameInput.value : item.querySelector(".feature-name").textContent,
        value: valueInput ? valueInput.value : item.querySelector(".feature-value").textContent,
      };
    });

    const payload = {
      name: planNameInput.value,
      badge: planBadgeInput.value,
      description: planDescInput.value,
      price: parseFloat(planMonthlyInput.value),
      yearly_price: parseFloat(planYearlyInput.value),
      is_active: planStatusInput.checked,
      display_order: parseInt(planOrderInput.value),
      features: features,
    };

    const url = isCreatingNew ? "/api/plans/create/" : `/api/plans/${currentPlanId}/update/`;

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify(payload),
    }).then((res) => {
      if (res.ok) {
        alert("Changes saved successfully!");
        location.reload();
      } else {
        alert("Failed to save changes.");
      }
    });
  });

  // Add new empty feature row
  addFeatureBtn.addEventListener("click", () => {
    const div = document.createElement("div");
    div.className = "feature-item";
    div.innerHTML = `
      <div class="feature-info">
        <div class="feature-details">
          <input type="text" class="form-control feature-name-input" placeholder="Feature Name" />
          <input type="text" class="form-control feature-value-input" placeholder="Feature Value" />
        </div>
      </div>
      <div class="feature-actions">
        <button class="btn-action btn-delete">Delete</button>
      </div>
    `;

    div.querySelector(".btn-delete").addEventListener("click", () => div.remove());
    featureList.appendChild(div);
  });

  function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + "=")) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  }
});

// Render active plans for users
fetch("/api/plans/active/")
  .then(response => response.json())
  .then(data => {
    const userPlanContainer = document.getElementById("user-plan-container");
    if (!userPlanContainer) return;
    userPlanContainer.innerHTML = "";
    data.plans.forEach(plan => {
      const div = document.createElement("div");
      div.className = "plan-card";
      div.innerHTML = `
        <h3>${plan.name}</h3>
        <p>${plan.description}</p>
        <p>Price: $${plan.price}</p>
      `;
      userPlanContainer.appendChild(div);
    });
  });
