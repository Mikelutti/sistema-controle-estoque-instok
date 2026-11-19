/* Cada carregamento inicia no tema escuro, antes da exibição da página. */
(() => {
    const root = document.documentElement;
    root.classList.replace("no-js", "js");
    root.dataset.theme = "dark";
})();
