function showPage(pageId) {

    // Hide all pages
    const pages = document.querySelectorAll(".page");

    pages.forEach(page => {
        page.classList.remove("active-page");
    });

    // Show selected page
    document.getElementById(pageId).classList.add("active-page");

    // Update active menu
    const items = document.querySelectorAll(".menu li");

    items.forEach(item => {
        item.classList.remove("active");
    });

    event.currentTarget.parentElement.classList.add("active");
}


// Sidebar Toggle

function toggleSidebar() {

    const sidebar = document.querySelector(".sidebar");
    const main = document.querySelector(".main-content");

    sidebar.classList.toggle("close");
    main.classList.toggle("expand");

}


// Open Dashboard by default

window.onload = function(){

    showPage("dashboardPage");

}