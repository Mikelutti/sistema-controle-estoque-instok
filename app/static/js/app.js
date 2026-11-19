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
        });
    }

    let selectedTheme = root.dataset.theme;
    let transition;
    themeButtons.forEach((button) => button.addEventListener("click", () => {
        selectedTheme = selectedTheme === "dark" ? "light" : "dark";
        const applyTheme = () => {
            root.dataset.theme = selectedTheme;
            updateThemeControls();
        };
        transition?.skipTransition();
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            applyTheme();
            return;
        }
        root.classList.add("theme-transition");
        if (!document.startViewTransition) {
            applyTheme();
            return;
        }
        const bounds = button.getBoundingClientRect();
        const x = bounds.left + bounds.width / 2;
        const y = bounds.top + bounds.height / 2;
        const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
        root.style.setProperty("--theme-origin", x + "px " + y + "px");
        root.style.setProperty("--theme-radius", Math.ceil(radius) + "px");
        transition = document.startViewTransition(applyTheme);
        const activeTransition = transition;
        activeTransition.finished.finally(() => {
            if (transition === activeTransition) root.classList.remove("theme-transition");
        });
    }));
    updateThemeControls();

    const passwordButton = document.querySelector("#toggle-password");
    const password = document.querySelector("#senha");
    if (passwordButton && password) {
        passwordButton.hidden = false;
        passwordButton.addEventListener("click", () => {
            const visible = password.type === "password";
            password.type = visible ? "text" : "password";
            passwordButton.querySelector('[data-password-icon="eye"]').hidden = visible;
            passwordButton.querySelector('[data-password-icon="eye-off"]').hidden = !visible;
            passwordButton.setAttribute("aria-label", visible ? "Ocultar senha" : "Mostrar senha");
            passwordButton.setAttribute("aria-pressed", String(visible));
        });
    }

    const sidebar = document.querySelector("#sidebar");
    const menuButton = document.querySelector("#menu-toggle");
    if (!sidebar || !menuButton) return;
    const search = document.querySelector(".page-search");
    if (search) {
        const field = search.querySelector("input");
        const list = search.querySelector("datalist");
        const pages = [...sidebar.querySelectorAll("nav a")];
        for (const page of pages) {
            const option = document.createElement("option");
            option.value = page.textContent.trim();
            list.append(option);
        }
        search.hidden = false;
        field.addEventListener("input", () => field.setCustomValidity(""));
        search.addEventListener("submit", event => {
            event.preventDefault();
            const query = field.value.trim().toLocaleLowerCase();
            const page = pages.find(link => link.textContent.trim().toLocaleLowerCase() === query);
            if (page) location.assign(page.href);
            else {
                field.setCustomValidity("Selecione uma página da lista.");
                field.reportValidity();
            }
        });
    }
    const closeButton = sidebar.querySelector(".sidebar-close");
    const overlay = document.querySelector(".menu-overlay");
    const content = document.querySelector(".content");
    const mobile = window.matchMedia("(max-width: 760px), (hover: none)");
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
