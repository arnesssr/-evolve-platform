document.addEventListener("DOMContentLoaded", function () {
  console.log("Sidebar JS loaded");
  
  const toggleBtn = document.getElementById("toggleBtn");
  const headerToggleBtn = document.getElementById("headerToggleBtn");
  const collapsedMenuBtn = document.getElementById("collapsedMenuBtn");
  const sidebar = document.getElementById("sidebar");
  const mainContent = document.querySelector(".main-content") || document.getElementById("mainContent");

  const isMobile = window.matchMedia("(max-width: 991.98px)").matches;

  console.log("Toggle button:", toggleBtn);
  console.log("Header toggle button:", headerToggleBtn);
  console.log("Sidebar:", sidebar);
  console.log("Main content:", mainContent);
  console.log("isMobile:", isMobile);

  // On mobile/tablet, we don't manage the sidebar via JS; Bootstrap Offcanvas or mobile menu handles navigation.
  if (isMobile) {
    if (mainContent) {
      mainContent.style.marginLeft = "0";
    }
    document.documentElement.classList.remove('sidebar-preload-collapsed');
    return; // exit early on mobile/tablet
  }

  // Check if sidebar was previously collapsed - default to false (expanded)
  const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true";
  
  // Clear any previous incorrect state
  if (localStorage.getItem("sidebarCollapsed") === null) {
    localStorage.setItem("sidebarCollapsed", "false");
  }
  
  if (sidebar && mainContent) {
    // Apply saved state (desktop defaults)
    if (isCollapsed) {
      sidebar.classList.add("collapsed");
      mainContent.classList.add("sidebar-collapsed");
      mainContent.style.marginLeft = "var(--sidebar-collapsed-width, 70px)";
    } else {
      mainContent.classList.remove("sidebar-collapsed");
      mainContent.style.marginLeft = "var(--sidebar-width, 260px)";
    }

    // Responsive correction: on small screens, content should span full width
    function applyResponsiveLayout() {
      if (window.matchMedia("(max-width: 991.98px)").matches) {
        // On mobile/tablet, sidebar is offcanvas; content margin should be 0
        mainContent.style.marginLeft = "0";
      } else {
        // On desktop, honor collapsed state
        if (sidebar.classList.contains("collapsed")) {
          mainContent.style.marginLeft = "var(--sidebar-collapsed-width, 70px)";
        } else {
          mainContent.style.marginLeft = "var(--sidebar-width, 260px)";
        }
      }
    }
    applyResponsiveLayout();
    window.addEventListener('resize', applyResponsiveLayout);
    
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
      // On desktop (>= lg), collapse/expand the fixed sidebar.
      // On mobile (< lg), allow Bootstrap Offcanvas (data attributes) to handle the toggle.
      if (window.matchMedia("(min-width: 992px)").matches) {
        e.preventDefault();
        e.stopPropagation();
        console.log("Header toggle button clicked (desktop)");
        toggleSidebar();
      } else {
        console.log("Header toggle button clicked (mobile) - letting Bootstrap Offcanvas handle it");
        // Do not prevent default so Bootstrap's data API can open the offcanvas
      }
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
