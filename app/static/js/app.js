/* Interacoes de apresentacao; formulários e navegacao usam o Flask. */
(() => {
    const root = document.documentElement;
    const themeButtons = document.querySelectorAll("[data-theme-toggle]");

    function updateThemeControls() {
        const dark = root.dataset.theme === "dark";
        themeButtons.forEach((button) => {
            button.hidden = false;
            button.setAttribute("aria-pressed", String(dark));
            button.setAttribute("aria-label", dark ? "Ativar tema claro" : "Ativar tema escuro");
            button.querySelector("[data-theme-icon]").textContent = dark ? "☀" : "☾";
            const label = button.querySelector("[data-theme-label]");
            if (label) label.textContent = dark ? "Tema claro" : "Tema escuro";
        });
    }

    themeButtons.forEach((button) => button.addEventListener("click", () => {
        const theme = root.dataset.theme === "dark" ? "light" : "dark";
        root.dataset.theme = theme;
        try { localStorage.setItem("instock-theme", theme); } catch { /* Preferencia apenas nesta pagina. */ }
        updateThemeControls();
    }));
    updateThemeControls();

    const passwordButton = document.querySelector("#toggle-password");
    const password = document.querySelector("#senha");
    if (passwordButton && password) {
        passwordButton.hidden = false;
        passwordButton.addEventListener("click", () => {
            const visible = password.type === "password";
            password.type = visible ? "text" : "password";
            passwordButton.setAttribute("aria-label", visible ? "Ocultar senha" : "Mostrar senha");
            passwordButton.setAttribute("aria-pressed", String(visible));
        });
    }

    const sidebar = document.querySelector("#sidebar");
    const menuButton = document.querySelector("#menu-toggle");
    if (!sidebar || !menuButton) return;
    const closeButton = sidebar.querySelector(".sidebar-close");
    const overlay = document.querySelector(".menu-overlay");
    const content = document.querySelector(".content");
    const mobile = window.matchMedia("(max-width: 760px)");
    let menuOpen = false;

    function setMenu(open, restoreFocus = false) {
        menuOpen = mobile.matches && open;
        document.body.classList.toggle("menu-open", menuOpen);
        menuButton.setAttribute("aria-expanded", String(menuOpen));
        overlay.hidden = !menuOpen;
        sidebar.inert = mobile.matches && !menuOpen;
        content.inert = menuOpen;
        if (menuOpen) closeButton.focus();
        else if (restoreFocus) menuButton.focus();
    }

    function syncViewport() {
        menuButton.hidden = !mobile.matches;
        closeButton.hidden = !mobile.matches;
        const focusWasInSidebar = sidebar.contains(document.activeElement);
        setMenu(false, mobile.matches && focusWasInSidebar);
    }

    menuButton.addEventListener("click", () => setMenu(!menuOpen));
    closeButton.addEventListener("click", () => setMenu(false, true));
    overlay.addEventListener("click", () => setMenu(false, true));
    document.addEventListener("keydown", (event) => {
        if (!menuOpen) return;
        if (event.key === "Escape") {
            event.preventDefault();
            setMenu(false, true);
        } else if (event.key === "Tab") {
            const controls = [...sidebar.querySelectorAll("a[href], button:not([disabled])")]
                .filter((element) => !element.hidden && element.getClientRects().length);
            const first = controls[0];
            const last = controls[controls.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }
    });
    mobile.addEventListener("change", syncViewport);
    syncViewport();
})();
