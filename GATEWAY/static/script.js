document.addEventListener("DOMContentLoaded", () => {

    const form = document.querySelector("form");

    const loading = document.getElementById("loading");

    const button = document.querySelector("button");

    form.addEventListener("submit", () => {

        loading.style.display = "block";

        button.disabled = true;

        button.innerHTML = "🔄 Analyzing...";

    });

});