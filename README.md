# GiroCar ERP

Sistema web acadêmico para apoiar a gestão de uma revenda de veículos. A aplicação reúne informações de estoque, vendas, pagamentos, manutenções, clientes, fornecedores, lojas e funcionários em uma interface construída com Streamlit.

![Status do projeto](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red)
![Banco de dados](https://img.shields.io/badge/Banco-Supabase%20%2F%20PostgreSQL-47c363)

## Sobre o projeto

O GiroCar ERP foi desenvolvido como projeto acadêmico para a disciplina de Gestão e Qualidade de Software (GQS), no curso de Análise e Desenvolvimento de Sistemas, sob orientação do professor Daniel Henrique Matos de Paiva.

O sistema busca apoiar a organização da operação de uma revenda, facilitando o acompanhamento dos veículos e de seu ciclo de preparação e venda. A proposta também se relaciona ao **Objetivo de Desenvolvimento Sustentável 12 (Consumo e Produção Responsáveis)**, ao incentivar o controle e a manutenção da frota.

## Funcionalidades

### Dashboard

- Exibe a quantidade de veículos disponíveis e em preparação.
- Calcula o capital investido nos veículos disponíveis e em preparação.
- Apresenta a quantidade de vendas e o lucro bruto no período selecionado.
- Mostra um gráfico de lucro por veículo e a fila de veículos em preparação.

### Gestão de veículos

- Cadastra veículos com dados de identificação, fabricação, aquisição, status e indicadores de risco.
- Associa o veículo a uma loja e a um fornecedor cadastrados.
- Consulta o estoque com filtros por placa, status e marca.
- Atualiza o status do veículo ou exclui um registro, respeitando vínculos existentes no banco.
- Consulta a Tabela FIPE por marca, modelo e ano.
- Permite registrar no histórico de um veículo da frota o valor consultado na FIPE.
- Exibe e filtra o histórico de avaliações.

### Comercial e vendas

- Exibe o histórico de vendas, com filtros por placa e faixa de valor.
- Registra uma venda associando veículo, cliente, funcionário, data e valor negociado.
- Atualiza para **Vendido** o status do veículo após a confirmação da venda.
- Registra pagamentos associados a uma venda, incluindo modalidade, valor, parcelas, instituição processadora e taxa de juros.
- Apresenta indicadores de quantidade de vendas, total negociado e ticket médio.

### Oficina e manutenções

- Registra ordens de serviço para veículos não vendidos.
- Armazena descrição, data e custo do serviço.
- Atualiza o status do veículo para **Em preparacao** após o registro da manutenção.
- Consulta o histórico com filtros por placa e período, além de indicadores de custo.

### Parceiros e administração

- Cadastra e consulta clientes, com pesquisa textual e filtro pelo estágio do funil de vendas.
- Cadastra e consulta fornecedores, com pesquisa por documento, nome ou telefone.
- Cadastra e consulta lojas, com pesquisa por CNPJ, nome ou endereço.
- Cadastra e consulta funcionários, com filtros por cargo e pesquisa textual.

## Tecnologias

- **Python** — linguagem da aplicação e das regras de negócio.
- **Streamlit** — interface web e navegação entre páginas.
- **Supabase** — conexão com o banco de dados PostgreSQL.
- **Pandas** — manipulação e apresentação de dados tabulares.
- **Requests** — chamadas à API pública da Tabela FIPE.
- **Pytest** — execução dos testes automatizados das regras de negócio.
- **Git e GitHub** — versionamento do projeto.

## Estrutura do repositório

```text
GiroCarERP/
├── 00_Dashboard.py       # Dashboard inicial
├── database.py           # Inicialização da conexão com o Supabase
├── regras_negocio.py     # Funções de regras de negócio
├── test_regras.py        # Testes automatizados das regras de negócio
├── pages/
│   ├── 01_Veiculos.py    # Gestão de veículos e consultas FIPE
│   ├── 02_Comercial.py   # Vendas e pagamentos
│   ├── 03_Manutencoes.py # Ordens de serviço e histórico
│   ├── 04_Parceiros.py   # Clientes e fornecedores
│   └── 05_Administracao.py # Lojas e funcionários
├── assets/
│   └── girocar.png       # Logo usada na interface
└── .streamlit/
    └── secrets.toml      # Credenciais locais (não versionar)
```

O Streamlit identifica automaticamente as páginas adicionais dentro da pasta `pages/`.

## Pré-requisitos

- Python 3.10 ou superior.
- Uma instância Supabase acessível.
- O esquema do banco de dados configurado previamente. O projeto consulta e grava dados, mas não inclui scripts de criação ou migração das tabelas.

## Como executar localmente

1. Clone o repositório e entre na pasta do projeto:

   ```bash
   git clone https://github.com/IcaroFeroliv/GiroCarERP.git
   cd GiroCarERP
   ```

2. Crie e ative um ambiente virtual:

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **Linux ou macOS:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   python -m pip install streamlit supabase pandas requests pytest
   ```

4. Configure as credenciais do Supabase. Crie `.streamlit/secrets.toml` na raiz do projeto:

   ```toml
   SUPABASE_URL = "https://seu-projeto.supabase.co"
   SUPABASE_KEY = "sua-chave-do-supabase"
   ```

   Use as credenciais apropriadas para o ambiente e **não compartilhe nem versione esse arquivo**. Para deploy no Streamlit Community Cloud, configure os mesmos nomes em **App settings → Secrets**.

5. Inicie a aplicação:

   ```bash
   streamlit run 00_Dashboard.py
   ```

   O Streamlit exibirá no terminal o endereço local da aplicação.

## Banco de dados

A aplicação espera que as tabelas e relacionamentos já existam no Supabase. As principais tabelas utilizadas são:

| Tabela | Finalidade |
|---|---|
| `veiculo` | Cadastro, status, aquisição e vínculos dos veículos |
| `transacao` | Vendas realizadas e seus dados comerciais |
| `pagamento` | Pagamentos associados às transações |
| `manutencao` | Ordens de serviço e custos de manutenção |
| `historico` | Avaliações FIPE vinculadas a veículos |
| `cliente` | Dados de clientes e estágio no funil de vendas |
| `fornecedor` | Dados e origem dos fornecedores |
| `loja` | Cadastro das lojas e filiais |
| `funcionario` | Funcionários, cargos e lojas vinculadas |

Os campos usados pela aplicação incluem identificadores como `placa`, `id_transacao`, `cpf_cnpj` e `matricula`, além de valores e status específicos de cada operação. Configure os tipos e as chaves estrangeiras de acordo com os dados enviados e consultados pelo código.

## Testes

Os testes automatizados disponíveis validam o cálculo de lucro bruto, a regra de elegibilidade para venda (RN01) e a formatação de valores monetários:

```bash
python -m pytest -v
```

## Regras de negócio

O módulo `regras_negocio.py` contém funções isoladas para cálculo do lucro bruto, validação da regra RN01 e formatação de moeda brasileira. Os testes correspondentes estão em `test_regras.py`.

## Observações

- As consultas FIPE dependem da disponibilidade da API externa.
- O banco precisa estar acessível e corretamente configurado para carregar ou salvar os dados.
- A aplicação registra mensagens e erros durante a execução para auxiliar no diagnóstico.
- A configuração de deploy depende das credenciais e do ambiente fornecidos ao Streamlit Community Cloud.

## Equipe de desenvolvimento

- **Ícaro** — arquitetura, banco de dados, dashboard e módulo de veículos.
- **Kaio** — interface visual (UI/UX), parceiros e administração.
- **Erick** — regras de negócio financeiras, módulo comercial, oficina e testes.

---

Projeto acadêmico desenvolvido em outubro de 2026 para composição da nota da Avaliação A3.
