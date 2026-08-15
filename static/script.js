 
function openPage() {

    const input = document.getElementById("pageName");
    const pageName = input.value.trim();

    if (!pageName) {
        alert("Please enter a page name.");
        return;
    }

    if (!/^[A-Za-z0-9_-]{1,50}$/.test(pageName)) {
        alert("Use only letters, numbers, hyphens (-), or underscores (_).");
        return;
    }

    window.location.href = "/" + pageName;
}