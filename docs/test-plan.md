# Plano de Testes — Swag Labs (saucedemo.com)

## 1. Objetivo
Validar, de ponta a ponta e pela interface, os fluxos críticos de um e-commerce:
autenticação, catálogo, carrinho e checkout — com cenários positivos e negativos.

## 2. Escopo
| Dentro do escopo | Fora do escopo |
|---|---|
| Login / logout / controle de acesso | Testes de carga e performance |
| Listagem, ordenação e detalhe de produtos | Testes de API (o site não expõe API pública) |
| Carrinho (adicionar, remover, persistência) | Acessibilidade (WCAG) e testes visuais |
| Checkout (validação de formulário, cálculo de imposto, conclusão) | Usuários `problem_user`, `error_user`, `visual_user` (próxima iteração) |

## 3. Estratégia
- **Ferramentas:** Python 3.12, pytest, Playwright (pytest-playwright), pytest-html, pytest-xdist.
- **Padrão de projeto:** Page Object Model — seletores e ações ficam em `pages/`; os testes só descrevem comportamento e asserções.
- **Seletores:** atributo `data-test` (configurado como test id) e papéis acessíveis (`get_by_role`). Nada de XPath frágil.
- **Esperas:** apenas as automáticas do Playwright (`expect(...)`), sem `sleep`.
- **Massa de dados:** centralizada em `data/test_data.py`; senha sobrescrevível via `SAUCE_PASSWORD`.
- **Isolamento:** cada teste usa um contexto de navegador novo, então os testes são independentes e podem rodar em paralelo.
- **Navegadores no CI:** Chromium e Firefox.

### Marcadores
| Marcador | Uso |
|---|---|
| `smoke` | Fluxos críticos — rodar a cada alteração (`pytest -m smoke`) |
| `regression` | Cobertura funcional completa |
| `negative` | Entradas inválidas e cenários de erro |
| `known_bug` | Defeitos reais documentados (`xfail` estrito) |

## 4. Casos de teste

### Autenticação — `tests/test_login.py`
| ID | Cenário | Tipo | Resultado esperado |
|---|---|---|---|
| LOGIN-01 | Login com credenciais válidas | Positivo · smoke | Redireciona para `/inventory.html`, título "Products" |
| LOGIN-02 | Usuário e senha vazios | Negativo | "Username is required" |
| LOGIN-03 | Sem usuário | Negativo | "Username is required" |
| LOGIN-04 | Sem senha | Negativo | "Password is required" |
| LOGIN-05 | Senha incorreta | Negativo | "Username and password do not match…" |
| LOGIN-06 | Usuário inexistente | Negativo | "Username and password do not match…" |
| LOGIN-07 | Usuário em maiúsculas (case-sensitive) | Negativo | "Username and password do not match…" |
| LOGIN-08 | Usuário bloqueado (`locked_out_user`) | Negativo | "Sorry, this user has been locked out." |
| LOGIN-09 | Fechar mensagem de erro | Negativo | Mensagem deixa de ser exibida |
| LOGIN-10 | Campo de senha mascarado | Segurança | `type="password"` |
| LOGIN-11 | Acesso direto a `/inventory.html` sem login | Negativo · segurança | Volta ao login com aviso de acesso restrito |
| LOGIN-12 | Logout | Positivo · smoke | Volta à tela de login com campos vazios |
| LOGIN-13 | Acesso após logout | Negativo · segurança | Sessão invalidada, acesso negado |

### Catálogo — `tests/test_inventory.py`
| ID | Cenário | Tipo | Resultado esperado |
|---|---|---|---|
| INV-01 | Listagem completa | Positivo · smoke | 6 produtos com os nomes esperados |
| INV-02 | Preços válidos | Positivo | Todos os preços > 0 |
| INV-03 | Ordenação padrão | Positivo | Nome A→Z |
| INV-04 a 07 | Ordenar por nome A→Z, Z→A, preço ↑, preço ↓ | Positivo | Lista na ordem correta |
| INV-08 | Detalhe do produto | Positivo | Mesmo nome e preço da listagem |
| INV-09 | Voltar do detalhe | Positivo | Retorna à vitrine com 6 produtos |

### Carrinho — `tests/test_cart.py`
| ID | Cenário | Tipo | Resultado esperado |
|---|---|---|---|
| CART-01 | Adicionar 1 produto | Positivo · smoke | Badge "1", botão vira "Remove" |
| CART-02 | Adicionar vários produtos | Positivo | Badge "3", carrinho lista os 3 |
| CART-03 | Adicionar pela página de detalhe | Positivo | Badge "1" |
| CART-04 | Remover pela vitrine | Positivo | Badge some, botão volta a "Add to cart" |
| CART-05 | Remover pelo carrinho | Positivo | Item removido, badge "1" |
| CART-06 | Persistência ao continuar comprando | Positivo | Itens mantidos |
| CART-07 | Persistência após recarregar a página | Positivo | Itens mantidos |
| CART-08 | Reset App State esvazia o carrinho | Positivo | Badge some, carrinho vazio |
| CART-09 | Reset App State restaura botões | **Bug conhecido** | Ver [BUG-002](bug-reports.md#bug-002--reset-app-state-não-restaura-os-botões-dos-produtos) |

### Checkout — `tests/test_checkout.py`
| ID | Cenário | Tipo | Resultado esperado |
|---|---|---|---|
| CHK-01 | Compra completa ponta a ponta | Positivo · smoke | Subtotal, imposto (8%) e total corretos; "Thank you for your order!" |
| CHK-02 | Subtotal = soma dos itens | Positivo | Valores batem |
| CHK-03 a 06 | Campos obrigatórios (todos vazios, sem nome, sem sobrenome, sem CEP) | Negativo | Mensagem de erro específica, permanece na etapa 1 |
| CHK-07 | Cancelar na etapa de informações | Positivo | Volta ao carrinho com itens |
| CHK-08 | Cancelar no resumo | Positivo | Volta à vitrine, carrinho mantido |
| CHK-09 | Voltar à loja após o pedido | Positivo | Vitrine com carrinho vazio |
| CHK-10 | Checkout com carrinho vazio deve ser bloqueado | **Bug conhecido** | Ver [BUG-001](bug-reports.md#bug-001--checkout-permitido-com-carrinho-vazio) |

## 5. Critérios de entrada e saída
- **Entrada:** site disponível; dependências instaladas.
- **Saída:** 100% dos testes `smoke` passando; nenhum teste `regression`/`negative` falhando; bugs conhecidos documentados.

## 6. Riscos
| Risco | Mitigação |
|---|---|
| Site público pode mudar sem aviso | Seletores por `data-test`; execução agendada diária no CI detecta quebras cedo |
| Instabilidade de rede (flaky) | Esperas automáticas do Playwright; trace e vídeo salvos em toda falha |
