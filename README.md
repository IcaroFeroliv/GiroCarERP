# GiroCar ERP

Sistema web de gestão para revenda de veículos desenvolvido em **Python** e **Streamlit**, com persistência em **Supabase (PostgreSQL)** e integração com a **API pública da Tabela FIPE**. A aplicação centraliza o controle de estoque, fluxo comercial, oficina/manutenções, CRM de parceiros, administração de filiais e auditoria gerencial, com controle de acesso baseado em perfis.

![Status do projeto](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Interface-Streamlit-FF4B4B)
![Supabase](https://img.shields.io/badge/Banco-Supabase%20%2F%20PostgreSQL-3ECF8E)
![Pytest](https://img.shields.io/badge/Testes-Pytest%20%2B%20Coverage-0A9EDC)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-lightgrey)

---

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Arquitetura e organização](#arquitetura-e-organiza%C3%A7%C3%A3o)
- [Estrutura do repositório](#estrutura-do-reposit%C3%B3rio)
- [Controle de acesso e perfis (RBAC)](#controle-de-acesso-e-perfis-rbac)
- [Módulos e funcionalidades](#m%C3%B3dulos-e-funcionalidades)
- [Regras de negócio](#regras-de-neg%C3%B3cio)
- [Tecnologias e integrações](#tecnologias-e-integra%C3%A7%C3%B5es)
- [Pré-requisitos](#pr%C3%A9-requisitos)
- [Instalação e execução local](#instala%C3%A7%C3%A3o-e-execu%C3%A7%C3%A3o-local)
- [Banco de dados (Supabase)](#banco-de-dados-supabase)
- [Testes automatizados e cobertura](#testes-automatizados-e-cobertura)
- [Observações operacionais](#observa%C3%A7%C3%B5es-operacionais)
- [Equipe e licença](#equipe-e-licen%C3%A7a)

---

## Sobre o projeto

O **GiroCar ERP** foi desenvolvido como projeto acadêmico para a disciplina de **Gestão e Qualidade de Software (GQS)** no curso de **Análise e Desenvolvimento de Sistemas**, sob orientação do professor Daniel Henrique Matos de Paiva.

O sistema apoia a operação de uma revenda de veículos desde a aquisição e preparação na oficina até a venda, o pagamento e a auditoria financeira. A iniciativa também dialoga com o **Objetivo de Desenvolvimento Sustentável 12 (Consumo e Produção Responsáveis)** ao estruturar o acompanhamento de manutenções e a vida útil da frota.

---

## Arquitetura e organização

A aplicação adota uma arquitetura modular orientada a domínio e separação de responsabilidades:

1. **Camada de Entrada e Orquestração (`00_Dashboard.py` e `pages/`)**:
   - Cada página atua como um *maestro* enxuto: configura o layout (`st.set_page_config`), executa a trava de segurança (`verificar_acesso`), valida a conexão com o banco e compõe os componentes visuais daquela rota.
2. **Camada de Apresentação (`components/<dominio>/`)**:
   - Componentes reutilizáveis de interface (cabeçalhos, formulários, filtros, tabelas, KPIs, abas e gráficos), isolados por contexto (`dashboard`, `veiculos`, `comercial`, `manutencoes`, `parceiros`, `administracao`).
3. **Camada de Domínio e Regras de Negócio (`components/regras_negocio/` e `regras_negocio.py`)**:
   - Funções puras e utilitários desacoplados da UI para cálculos financeiros, validação de documentos, autenticação, auditoria, integração com a API FIPE, filtros tabulares e tratamento padronizado de erros.
4. **Camada de Persistência (`database.py`)**:
   - Inicializa e mantém em cache (`@st.cache_resource`) o cliente oficial do Supabase utilizando `st.secrets`.

---

## Estrutura do repositório

```text
GiroCarERP/
├── 00_Dashboard.py                  # Ponto de entrada: login, barra de sessão e Dashboard Executivo / Portal Vendedor
├── database.py                      # Conexão em cache com o Supabase
├── regras_negocio.py                # Núcleo de regras financeiras, logísticas, CRM e crédito
├── test_regras.py                   # Suíte parametrizada de testes unitários (112 casos)
├── pyproject.toml                   # Configuração do Pytest e Coverage (branch coverage)
├── LICENSE                          # Licença MIT
├── assets/
│   └── girocar.png                  # Logotipo exibido na interface e favicon
├── pages/                           # Páginas multipage reconhecidas automaticamente pelo Streamlit
│   ├── 01_Veiculos.py               # Consulta, cadastro, Tabela FIPE e histórico de avaliações
│   ├── 02_Comercial.py              # Indicadores comerciais, histórico, registro de vendas e pagamentos
│   ├── 03_Manutencoes.py            # Histórico de oficina e abertura de ordens de serviço
│   ├── 04_Parceiros.py              # CRM de clientes e gestão de fornecedores
│   └── 05_Administracao.py          # Gestão de lojas (filiais) e funcionários
├── components/
│   ├── administracao/               # Abas, formulários e consultas de lojas e funcionários
│   ├── comercial/                   # KPIs, abas, formulários e consultas de vendas e pagamentos
│   ├── dashboard/                   # Login, portal do vendedor, KPIs, gráficos, oficina e auditoria
│   ├── manutencoes/                 # KPIs e abas de histórico e registro de manutenções
│   ├── parceiros/                   # Abas, formulários e consultas de clientes e fornecedores
│   ├── veiculos/                    # Abas, filtros, tabela, ações rápidas e vínculo FIPE
│   └── regras_negocio/              # Autenticação, RBAC, FIPE, auditoria, cálculos, filtros e formatadores
└── tests/
    └── ui/                          # Testes automatizados de páginas e componentes com mock do Streamlit
        ├── conftest.py              # Fixtures (mock_st e DummyContextManager)
        ├── test_pages.py
        ├── test_dashboard.py
        ├── test_veiculos.py
        ├── test_comercial.py
        ├── test_manutencoes.py
        ├── test_parceiros.py
        └── test_administracao.py
```

---

## Controle de acesso e perfis (RBAC)

A autenticação é gerenciada por `components/dashboard/tela_login.py` e `components/regras_negocio/autenticacao.py`, enquanto a proteção das rotas internas é aplicada no topo de cada arquivo em `pages/` via `verificar_acesso()` (`components/regras_negocio/trava_seguranca.py`):

| Perfil | Forma de Autenticação | Acesso Permitido |
|---|---|---|
| **Gerente** | E-mail autorizado em `CREDENCIAIS_GERENTES` e senha correspondente | Acesso irrestrito ao **Dashboard Executivo**, auditoria de vendas e todas as páginas (`01` a `05`) |
| **Vendedor** | Nome completo (normalizado sem espaços/acentos) e **matrícula** como senha, validados na tabela `funcionario` | Redirecionado ao **Portal do Vendedor** na página inicial, com acesso liberado apenas para `01_Veiculos.py`, `02_Comercial.py` e `03_Manutencoes.py` |

---

## Módulos e funcionalidades

### 1. Dashboard (`00_Dashboard.py`)
- **KPIs de Estoque**: contagem de veículos `Disponivel` e `Em preparacao`, além do capital total investido nesses status.
- **Análise de Vendas e Lucratividade**: filtro por período, cálculo de lucro bruto, quantidade vendida e gráfico de lucratividade por veículo.
- **Monitoramento de Oficina**: fila de veículos atualmente em preparação.
- **Seção de Auditoria**: cruzamento de dados de `transacao`, `veiculo`, `cliente` e `funcionario` para rastreabilidade completa das vendas.

### 2. Veículos (`pages/01_Veiculos.py`)
- **Consultar e Gerenciar**: filtros por placa, status e marca, tabela interativa e ações rápidas de atualização de status ou exclusão (respeitando integridade referencial no banco).
- **Cadastrar Veículo**: registro de dados do veículo com vínculo a uma loja e a um fornecedor cadastrados.
- **Consulta Tabela FIPE**: consulta em tempo real por marca, modelo e ano na API pública da FIPE (`parallelum.com.br`), com opção de vincular a avaliação ao histórico do veículo.
- **Histórico de Avaliações**: consulta e filtragem dos registros salvos na tabela `historico`.

### 3. Comercial (`pages/02_Comercial.py`)
- **Indicadores Comerciais**: total de vendas, faturamento negociado e ticket médio.
- **Histórico de Vendas**: visualização e filtragem por placa e faixa de valor.
- **Registrar Venda**: associa veículo com status `Disponivel`, cliente, funcionário, data e valor final negociado, atualizando o status do veículo para `Vendido`.
- **Lançar Pagamento**: registro de pagamentos vinculados a uma transação (modalidade, valor, parcelas, instituição processadora e taxa de juros).

### 4. Manutenções (`pages/03_Manutencoes.py`)
- **Histórico de Serviços**: listagem com filtros por placa e período, além de indicadores de custo de oficina.
- **Registrar Manutenção**: abertura de ordem de serviço para veículos não vendidos, atualizando automaticamente o status do veículo para `Em preparacao`.

### 5. Parceiros (`pages/04_Parceiros.py`)
- **Clientes (CRM)**: cadastro e pesquisa de clientes com filtro por estágio no funil de vendas.
- **Fornecedores**: cadastro e consulta por documento, nome ou telefone.

### 6. Administração (`pages/05_Administracao.py`)
- **Lojas (Filiais)**: cadastro e consulta de lojas por CNPJ, nome ou endereço.
- **Funcionários**: cadastro e consulta de colaboradores com filtro por cargo e vínculo com loja.

---

## Regras de negócio

O arquivo `regras_negocio.py` centraliza funções isoladas para regras de negócio e validação unitária:

- `formatar_moeda(valor)` — formatação monetária no padrão brasileiro (`R$ 1.500,50`) com tratamento de nulos e tipos inválidos.
- `limpar_valor_fipe(valor_str)` — conversão de strings monetárias retornadas pela API FIPE para `float`.
- `calcular_lucro_bruto(valor_venda, valor_compra, custos_oficina=0)` — apuração de lucro bruto deduzindo aquisição e custos de oficina.
- `validar_rn01_venda(status_veiculo)` — **RN01 (Bloqueio Logístico)**: permite faturamento apenas para veículos com status `Disponivel` / `Disponível`.
- `calcular_comissao(valor_venda, cargo)` — cálculo de comissão por cargo (`1%` para `Vendedor` e `1.5%` para `Gerente`).
- `limpar_e_validar_documento(doc)` — sanitização de máscara e validação estrutural de CPF (11 dígitos) e CNPJ (14 dígitos).
- `calcular_depreciacao_estoque(valor_fipe, dias_patio)` — aplica remarcação automática de `5%` para veículos com mais de `90` dias no pátio.
- `validar_financiamento(ano_veiculo, score_cliente)` — avaliação de crédito considerando idade máxima do veículo (`15` anos) e score mínimo (`500`).

---

## Tecnologias e integrações

- **Python 3.10+**
- **Streamlit** — framework web e roteamento multipage
- **Supabase (`supabase`)** — cliente Python para integração com PostgreSQL
- **Pandas** — transformação, cruzamento e exibição de DataFrames
- **Requests** — consumo da API REST pública da Tabela FIPE (`https://parallelum.com.br/fipe/api/v1/carros`)
- **Pytest & pytest-cov** — suíte de testes unitários, testes de UI com mocks e medição de cobertura de branches

---

## Pré-requisitos

- **Python 3.10** ou superior instalado.
- Projeto ativo no **Supabase** com URL e chave de acesso (`anon` ou `service_role`, conforme políticas RLS configuradas).
- Esquema de tabelas previamente criado no PostgreSQL do Supabase (o repositório não inclui scripts SQL de migração/DDL).

---

## Instalação e execução local

1. **Clone o repositório e acesse o diretório:**

   ```bash
   git clone https://github.com/IcaroFeroliv/GiroCarERP.git
   cd GiroCarERP
   ```

2. **Crie e ative um ambiente virtual:**

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **Linux / macOS:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências:**

   ```bash
   python -m pip install streamlit supabase pandas requests pytest pytest-cov
   ```

4. **Configure as credenciais do Supabase:**

   Crie o arquivo `.streamlit/secrets.toml` na raiz do projeto (este arquivo já está listado no `.gitignore` e não deve ser versionado):

   ```toml
   SUPABASE_URL = "https://seu-projeto.supabase.co"
   SUPABASE_KEY = "sua-chave-do-supabase"
   ```

   > Para deploy no **Streamlit Community Cloud**, cadastre as mesmas chaves em **App settings → Secrets**.

5. **Inicie a aplicação:**

   ```bash
   streamlit run 00_Dashboard.py
   ```

---

## Banco de dados (Supabase)

A aplicação interage com as seguintes tabelas no PostgreSQL via Supabase:

| Tabela | Finalidade |
|---|---|
| `veiculo` | Cadastro, placa, modelo, aquisição, status (`Disponivel`, `Em preparacao`, `Vendido`) e vínculos |
| `transacao` | Registro de vendas realizadas (data, veículo, cliente, vendedor e valor negociado) |
| `pagamento` | Pagamentos vinculados às transações comerciais |
| `manutencao` | Ordens de serviço, descrições, datas e custos de oficina |
| `historico` | Histórico de avaliações consultadas na Tabela FIPE |
| `cliente` | Dados cadastrais de clientes (`cpf_cnpj`, `nome_completo`) e funil de vendas |
| `fornecedor` | Dados e origem dos fornecedores |
| `loja` | Cadastro das lojas e filiais |
| `funcionario` | Colaboradores (`matricula`, `nome`, cargo e loja vinculada) |

---

## Testes automatizados e cobertura

O projeto possui configuração centralizada no arquivo `pyproject.toml`:

- `testpaths = ["tests", "test_regras.py"]`
- Cobertura de branches habilitada (`branch = true`), com geração de relatório no terminal (`term-missing`) e em HTML (`htmlcov/`).

Para executar toda a suíte de testes (regras de negócio + componentes de UI com mocks do Streamlit):

```bash
python -m pytest -v
```

Para executar apenas os testes unitários das regras de negócio sem relatório de cobertura:

```bash
python -m pytest test_regras.py -v --no-cov
```

---

## Observações operacionais

- As consultas da Tabela FIPE dependem da disponibilidade do serviço externo `parallelum.com.br`.
- Caso a conexão com o Supabase falhe ou `secrets.toml` esteja ausente, a aplicação exibe mensagens orientativas e interrompe o carregamento das páginas protegidas.
- Logs detalhados de exceções são emitidos via módulo padrão `logging` do Python e exibidos em expanders técnicos quando habilitado nos módulos.

---

## Equipe e licença

- **Ícaro** — arquitetura, banco de dados, dashboard e módulo de veículos.
- **Kaio** — interface visual (UI/UX), parceiros e administração.
- **Erick** — regras de negócio financeiras, módulo comercial, oficina e testes.

Distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
