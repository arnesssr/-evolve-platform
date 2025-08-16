document.addEventListener("DOMContentLoaded", function () {
  console.log("Sidebar JS loaded");
  
  const toggleBtn = document.getElementById("toggleBtn");
  const sidebar = document.getElementById("sidebar");
  const mainContent = document.querySelector(".main-content");

  console.log("Toggle button:", toggleBtn);
  console.log("Sidebar:", sidebar);
  console.log("Main content:", mainContent);

  // Check if sidebar was previously collapsed
  const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true";
  
  if (sidebar && mainContent) {
    // Apply saved state
    if (isCollapsed) {
      sidebar.classList.add("collapsed");
      mainContent.style.marginLeft = "70px";
    } else {
      mainContent.style.marginLeft = "260px";
    }
  }

  if (toggleBtn && sidebar && mainContent) {
    console.log("Adding click event listener");
    
    toggleBtn.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      console.log("Toggle button clicked");
      sidebar.classList.toggle("collapsed");
      
      // Update main content margin when sidebar collapses
      if (sidebar.classList.contains("collapsed")) {
        mainContent.style.marginLeft = "70px";
        localStorage.setItem("sidebarCollapsed", "true");
      } else {
        mainContent.style.marginLeft = "260px";
        localStorage.setItem("sidebarCollapsed", "false");
      }
    });
  } else {
    console.error("Missing elements:", {
      toggleBtn: !!toggleBtn,
      sidebar: !!sidebar,
      mainContent: !!mainContent
    });
  }
});
