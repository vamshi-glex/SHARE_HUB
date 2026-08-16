function openPage() {

    const input = document.getElementById("pageName");
    const pageName = input.value.trim();

    // Remove previous error
    const oldError = document.querySelector(".page-error");
    if (oldError) {
        oldError.remove();
    }

    if (!pageName) {

        showPageError(
            "Please enter a page name."
        );

        input.focus();
        return;
    }

    if (!/^[A-Za-z0-9_-]{1,50}$/.test(pageName)) {

        showPageError(
            "Use only letters, numbers, hyphens (-), or underscores (_)."
        );

        input.focus();
        return;
    }

    window.location.href = "/" + pageName;
}


function showPageError(message) {

    const inputGroup =
        document.querySelector(".page-input-group");

    const error =
        document.createElement("p");

    error.className = "page-error";
    error.textContent = message;

    inputGroup.insertAdjacentElement(
        "afterend",
        error
    );
}