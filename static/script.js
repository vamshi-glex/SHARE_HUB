function openPage() {

    const pageName = document.getElementById("pageName").value.trim();

    if (!pageName) {
        alert("Please enter a page name.");
        return;
    }

    window.location.href = "/" + pageName;
}