/* Somente preferencia visual. Dados e autenticacao pertencem ao servidor. */
(() => {
    const root = document.documentElement;
    root.classList.replace("no-js", "js");
    let theme = "light";
    try {
        if (localStorage.getItem("instock-theme") === "dark") theme = "dark";
    } catch {
        // O login permanece utilizavel quando o navegador bloqueia armazenamento.
    }
    root.dataset.theme = theme;
})();
