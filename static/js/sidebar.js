document.addEventListener("DOMContentLoaded", function () {
  console.log("Sidebar JS loaded");
  
  const toggleBtn = document.getElementById("toggleBtn");
  const headerToggleBtn = document.getElementById("headerToggleBtn");
  const collapsedMenuBtn = document.getElementById("collapsedMenuBtn");
  const sidebar = document.getElementById("sidebar");
  const mainContent = document.querySelector(".main-content") || document.getElementById("mainContent");

  console.log("Toggle button:", toggleBtn);
  console.log("Header toggle button:", headerToggleBtn);
  console.log("Sidebar:", sidebar);
  console.log("Main content:", mainContent);

  // Check if sidebar was previously collapsed - default to false (expanded)
  const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true";
  
  // Clear any previous incorrect state
  if (localStorage.getItem("sidebarCollapsed") === null) {
    localStorage.setItem("sidebarCollapsed", "false");
  }
  
  if (sidebar && mainContent) {
    // Apply saved state
    if (isCollapsed) {
      sidebar.classList.add("collapsed");
      mainContent.classList.add("sidebar-collapsed");
      // Use CSS variables for consistency
      mainContent.style.marginLeft = "var(--sidebar-collapsed-width, 70px)";
    } else {
      mainContent.classList.remove("sidebar-collapsed");
      mainContent.style.marginLeft = "var(--sidebar-width, 260px)";
    }
    
    // Remove preload class after state is applied
    document.documentElement.classList.remove('sidebar-preload-collapsed');
  }

  // Function to toggle sidebar
  function toggleSidebar() {
    sidebar.classList.toggle("collapsed");
    mainContent.classList.toggle("sidebar-collapsed");
    
    // Update main content margin when sidebar collapses
    if (sidebar.classList.contains("collapsed")) {
      mainContent.style.marginLeft = "var(--sidebar-collapsed-width, 70px)";
      localStorage.setItem("sidebarCollapsed", "true");
      
      // Rotate toggle button icon if it exists
      if (toggleBtn) {
        const icon = toggleBtn.querySelector('i');
        if (icon) {
          icon.style.transform = "rotate(90deg)";
        }
      }
    } else {
      mainContent.style.marginLeft = "var(--sidebar-width, 260px)";
      localStorage.setItem("sidebarCollapsed", "false");
      
      // Reset toggle button icon if it exists
      if (toggleBtn) {
        const icon = toggleBtn.querySelector('i');
        if (icon) {
          icon.style.transform = "rotate(0deg)";
        }
      }
    }
  }
  
  // Add click listener to sidebar toggle button (if it exists)
  if (toggleBtn && sidebar && mainContent) {
    console.log("Adding click event listener to sidebar toggle");
    
    toggleBtn.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      console.log("Toggle button clicked");
      toggleSidebar();
    });
  }
  
  // Add click listener to header toggle button
  if (headerToggleBtn && sidebar && mainContent) {
    console.log("Adding click event listener to header toggle");
    
    headerToggleBtn.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      console.log("Header toggle button clicked");
      toggleSidebar();
    });
  }
  
  // Add click listener to collapsed menu button
  if (collapsedMenuBtn && sidebar && mainContent) {
    console.log("Adding click event listener to collapsed menu button");
    
    collapsedMenuBtn.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      console.log("Collapsed menu button clicked");
      toggleSidebar();
    });
  }
  
  if (!toggleBtn && !headerToggleBtn && !collapsedMenuBtn) {
    console.error("Missing elements:", {
      toggleBtn: !!toggleBtn,
      headerToggleBtn: !!headerToggleBtn,
      collapsedMenuBtn: !!collapsedMenuBtn,
      sidebar: !!sidebar,
      mainContent: !!mainContent
    });
  }
});
