"""Filtros, apresentação tabular e exportação do mesmo conjunto de resultados."""
import csv
import io
from datetime import date
from app.repositories.relatorio_repository import consultar
from app.services.cadastro_service import inteiro
from app.services.alerta_service import obter_status_estoque

COLUNAS = {
    'movimentacoes': [('id','Registro'),('data_hora','Data (UTC)'),('tipo','Tipo'),
        ('codigo','Código'),('produto','Produto'),('categoria','Categoria'),
        ('quantidade','Quantidade'),('origem','Origem'),('destino','Destino'),
        ('responsavel','Responsável'),('observacao','Motivo')],
    'estoque': [('codigo','Código'),('produto','Produto'),('categoria','Categoria'),
        ('status','Situação cadastral'),('setor','Setor'),('quantidade','Quantidade'),
        ('estoque_minimo','Mínimo global do produto')],
    'alertas': [('codigo','Código'),('produto','Produto'),('categoria','Categoria'),
        ('quantidade','Saldo total'),('estoque_minimo','Mínimo'),('classificacao','Alerta')]
}


def validar_filtros(args):
    f = {k: args.get(k,'').strip() for k in ['relatorio','inicio','fim','tipo']}
    f['relatorio'] = f['relatorio'] or 'movimentacoes'
    if f['relatorio'] not in COLUNAS:
        raise ValueError('Selecione um relatório válido.')
    for k in ['produto_id','setor_id','categoria_id']:
        valor=args.get(k,'').strip()
        f[k]=inteiro(valor,k,1) if valor else None
    for k in ['inicio','fim']:
        if f[k]:
            try:
                if date.fromisoformat(f[k]).isoformat()!=f[k]:
                    raise ValueError()
            except ValueError:
                raise ValueError('Informe datas válidas no formato ano-mês-dia.') from None
    if f['inicio'] and f['fim'] and f['inicio']>f['fim']:
        raise ValueError('A data inicial não pode ser posterior à final.')
    if f['tipo'] not in ('','ENTRADA','SAIDA','TRANSFERENCIA'):
        raise ValueError('Selecione um tipo de movimentação válido.')
    if f['relatorio']!='movimentacoes' and any(f[k] for k in ['inicio','fim','tipo']):
        raise ValueError('Período e tipo são filtros exclusivos de movimentações.')
    if f['relatorio']=='alertas' and f['setor_id'] is not None:
        raise ValueError('Alertas consideram todos os setores. Remova o filtro de setor.')
    return f


def gerar_relatorio(args):
    filtros=validar_filtros(args)
    registros=consultar(filtros)
    if filtros['relatorio']=='alertas':
        produtos={}
        for row in registros:
            if row['id'] not in produtos:
                produtos[row['id']]={**row,'quantidade':0}
            produtos[row['id']]['quantidade']+=row['quantidade']
        registros=[]
        for row in produtos.values():
            row['classificacao']=obter_status_estoque(row['quantidade'],row['estoque_minimo'])
            if row['classificacao']!='ESTOQUE NORMAL':
                registros.append(row)
    return dict(filtros=filtros,colunas=COLUNAS[filtros['relatorio']],registros=registros)


def gerar_csv(relatorio):
    def seguro(valor):
        if valor is None:
            return ''
        texto=str(valor)
        if texto.lstrip().startswith(('=','+','-','@')) or texto.startswith(('\t','\r','\n')):
            return "'"+texto
        return texto
    arquivo=io.StringIO(newline='')
    writer=csv.writer(arquivo,delimiter=';')
    writer.writerow([rotulo for _,rotulo in relatorio['colunas']])
    for row in relatorio['registros']:
        writer.writerow([seguro(row[chave]) for chave,_ in relatorio['colunas']])
    return ('\ufeff'+arquivo.getvalue()).encode('utf-8')
