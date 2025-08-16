document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("user-plan-container");
  const toggle = document.getElementById("billingToggle");

  // Get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrfToken = getCookie("csrftoken");
  const createOrderUrl = document.body.getAttribute("data-create-order-url");

  // Fetch and render plans
  function fetchPlans() {
    fetch("/api/plans/active/?t=" + new Date().getTime())
      .then(res => res.json())
      .then(data => renderPlans(data.plans))
      .catch(err => {
        container.innerHTML = "<p>Error loading plans.</p>";
        console.error(err);
      });
  }

  // Render each plan card and attach payment logic
  function renderPlans(plans) {
    container.innerHTML = "";

    if (!plans || plans.length === 0) {
      container.innerHTML = "<p>No active plans available.</p>";
      return;
    }

    plans.forEach(plan => {
      const col = document.createElement("div");
      col.className = "col-md-4 d-flex";

      const isYearly = toggle.checked;
      const price = isYearly ? plan.yearly_price : plan.price;

      const card = document.createElement("div");
      card.className = "plan-card flex-fill";

      card.innerHTML = `
        <h4 class="text-center">${plan.name}
          ${plan.badge ? `<span class="badge-label">${plan.badge}</span>` : ""}
        </h4>
        <p class="text-center price">
          <span class="currency">KSh.</span>${parseFloat(price).toFixed(0)}
          <span class="interval">/ ${isYearly ? "year" : "month"}</span>
        </p>
        <ul class="feature-list">
          ${plan.features.map(f => `<li>&#10003; ${f.name}: ${f.value}</li>`).join("")}
        </ul>
        <div class="card-footer mt-3">
          <form method="POST" action="${createOrderUrl}">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <input type="hidden" name="amount" value="${parseFloat(price).toFixed(0)}">
            <button type="submit" class="btn btn-primary purchase-btn">Purchase Plan</button>
          </form>
        </div>
      `;

      // Attach event listener to the form to override default POST behavior
      const form = card.querySelector("form");
      form.addEventListener("submit", function (e) {
        e.preventDefault(); // Prevent page reload

        const formData = new FormData(form);

        fetch(createOrderUrl, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
          },
          body: formData,
        })
          .then(res => res.json())
          .then(data => {
            if (data.redirect_url) {
              // Redirect user directly to Pesapal URL
              window.location.href = data.redirect_url;
            } else {
              alert("Payment failed or redirect URL missing.");
            }
          })
          .catch(err => {
            console.error("Payment error:", err);
            alert("An error occurred while processing payment.");
          });
      });

      col.appendChild(card);
      container.appendChild(col);
    });
  }

  // Reload plans when billing toggle changes
  toggle.addEventListener("change", fetchPlans);

  // Initial load
  fetchPlans();
});
