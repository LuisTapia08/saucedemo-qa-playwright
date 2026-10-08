# Saucedemo QA — Playwright + pytest

![E2E Tests](https://github.com/LuisTapia08/saucedemo-qa-playwright/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![Playwright](https://img.shields.io/badge/playwright-1.63-2EAD33)

Suíte de testes E2E automatizados para o [Swag Labs (saucedemo.com)](https://www.saucedemo.com),
um e-commerce de demonstração. O projeto cobre os fluxos críticos de compra com cenários
**positivos e negativos**, usa **Page Object Model**, gera **relatório HTML** com screenshot
das falhas e roda no **GitHub Actions** a cada push, em Chromium e Firefox.

> Durante a exploração do sistema foram encontrados **2 defeitos reais**, documentados em
> [`docs/bug-reports.md`](docs/bug-reports.md) e cobertos por testes `xfail` estritos.

## Destaques

- **41 testes** em 4 áreas: login, catálogo, carrinho e checkout ([plano de testes](docs/test-plan.md))
- **Page Object Model** — os testes descrevem *o quê*; as páginas sabem *como*
- **Seletores estáveis** por `data-test` e papéis acessíveis, sem XPath e sem `sleep`
- **Testes parametrizados** para os cenários negativos (7 variações de login inválido, 4 de checkout)
- **Validação de regra de negócio:** subtotal, imposto de 8% e total do pedido
- **Bugs documentados como testes:** `xfail(strict=True)` — se o bug for corrigido, o CI avisa
- **Evidências automáticas:** screenshot embutido no relatório + vídeo e trace do Playwright em toda falha
- **CI/CD:** lint (ruff) → testes em paralelo (pytest-xdist) em 2 navegadores → relatórios como artefatos;
  também roda diariamente para detectar mudanças no site

## Estrutura

```
saucedemo-qa-playwright/
├── pages/                    # Page Objects
│   ├── base_page.py          # header, menu, carrinho e utilitários comuns
│   ├── login_page.py
│   ├── inventory_page.py     # vitrine: listar, ordenar, adicionar ao carrinho
│   ├── product_page.py       # detalhe do produto
│   ├── cart_page.py
│   └── checkout_page.py      # informações → resumo → confirmação
├── tests/
│   ├── conftest.py           # fixtures e hook do screenshot no relatório
│   ├── test_login.py
│   ├── test_inventory.py
│   ├── test_cart.py
│   └── test_checkout.py
├── data/test_data.py         # usuários, produtos e mensagens esperadas
├── docs/
│   ├── test-plan.md          # estratégia e casos de teste (IDs)
│   └── bug-reports.md        # defeitos encontrados
├── .github/workflows/tests.yml
├── pytest.ini
└── requirements.txt
```

## Como rodar

Pré-requisito: Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    |    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

```bash
pytest                         # suíte completa (relatório em reports/report.html)
pytest -m smoke                # só os fluxos críticos
pytest -m negative             # só cenários negativos
pytest -n 4                    # em paralelo
pytest --headed --slowmo 500   # vendo o navegador
pytest --browser firefox       # outro navegador (instale antes com playwright install firefox)
```

Para investigar uma falha, abra o trace gerado em `test-results/`:

```bash
python -m playwright show-trace test-results/<pasta-do-teste>/trace.zip
```

## Exemplo de teste

```python
@pytest.mark.smoke
def test_complete_purchase_end_to_end(inventory_page: InventoryPage):
    expected_prices = [inventory_page.price_of(BACKPACK), inventory_page.price_of(BIKE_LIGHT)]
    cart = inventory_page.add_to_cart(BACKPACK, BIKE_LIGHT).go_to_cart()

    overview = cart.checkout().continue_with(DEFAULT_CUSTOMER)

    subtotal = round(sum(expected_prices), 2)
    tax = round(subtotal * TAX_RATE, 2)
    assert overview.subtotal() == subtotal
    assert overview.tax() == tax
    assert overview.total() == round(subtotal + tax, 2)

    complete = overview.finish()
    expect(complete.header).to_have_text("Thank you for your order!")
```

## Relatório

Cada execução gera `reports/report.html` (arquivo único, abre em qualquer navegador).
No GitHub Actions, o relatório de cada navegador fica disponível em
**Actions → execução → Artifacts** (`report-chromium`, `report-firefox`), e um resumo
com o total de testes aparece na própria página da execução.

## Decisões técnicas

| Decisão | Motivo |
|---|---|
| `pytest-playwright` em vez de Selenium | Esperas automáticas, trace viewer, contexto isolado por teste e execução mais rápida |
| Asserções nos testes, não nas páginas | Page Objects reutilizáveis; o teste deixa claro o que está sendo verificado |
| `expect()` do Playwright | Re-tenta até o timeout, eliminando testes intermitentes por timing |
| `xfail(strict=True)` para bugs | O bug fica visível no relatório sem quebrar o pipeline, e o CI avisa quando for corrigido |
| Senha via `SAUCE_PASSWORD` (opcional) | Prática de não depender de segredos fixos no código |

## Próximos passos

- Cobrir `problem_user`, `error_user` e `performance_glitch_user`
- Testes de acessibilidade com `axe-core`
- Testes de regressão visual
- Publicar o relatório no GitHub Pages

---

Autor: **Luís Tápia** · [GitHub](https://github.com/LuisTapia08)
