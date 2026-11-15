const seletorRelatorio = document.getElementById('relatorio');
function atualizarFiltros() {
    const movimentacoes = seletorRelatorio.value === 'movimentacoes';
    for (const nome of ['inicio', 'fim', 'tipo', 'setor_id']) {
        const campo = seletorRelatorio.form.elements[nome];
        campo.disabled = nome === 'setor_id' ? seletorRelatorio.value === 'alertas' : !movimentacoes;
        campo.parentElement.hidden = campo.disabled;
    }
}
seletorRelatorio.addEventListener('change', atualizarFiltros);
atualizarFiltros();
