# Bug Reports

Defeitos reais encontrados durante a exploração do [Swag Labs (saucedemo.com)](https://www.saucedemo.com).
Cada um está coberto por um teste marcado com `@pytest.mark.known_bug` + `xfail(strict=True)`:
o teste documenta o **comportamento esperado** e "falha como previsto" enquanto o bug existir.
Se o bug for corrigido, o teste passa a dar `XPASS` e o pytest acusa erro — sinal para remover o `xfail`.

---

## BUG-001 — Checkout permitido com carrinho vazio

| Campo | Valor |
|---|---|
| **Severidade** | Alta |
| **Prioridade** | Alta |
| **Ambiente** | https://www.saucedemo.com · Chromium |
| **Usuário** | `standard_user` |
| **Teste automatizado** | `tests/test_checkout.py::test_checkout_is_blocked_with_empty_cart` |

**Passos para reproduzir**
1. Fazer login com `standard_user` / `secret_sauce`.
2. Sem adicionar produtos, clicar no ícone do carrinho.
3. Clicar em **Checkout**.
4. Preencher First Name, Last Name e Postal Code e clicar em **Continue**.
5. Clicar em **Finish**.

**Resultado esperado:** o botão Checkout deve estar desabilitado (ou exibir uma mensagem) quando o carrinho está vazio; nenhum pedido deve ser criado.

**Resultado obtido:** o fluxo segue normalmente, o resumo mostra `Total: $0.00` e a tela "Thank you for your order!" é exibida — um pedido vazio é concluído.

**Impacto:** pedidos inválidos no sistema e dados poluídos em relatórios de vendas.

---

## BUG-002 — "Reset App State" não restaura os botões dos produtos

| Campo | Valor |
|---|---|
| **Severidade** | Média |
| **Prioridade** | Média |
| **Ambiente** | https://www.saucedemo.com · Chromium |
| **Usuário** | `standard_user` |
| **Teste automatizado** | `tests/test_cart.py::test_reset_app_state_restores_add_buttons` |

**Passos para reproduzir**
1. Fazer login com `standard_user` / `secret_sauce`.
2. Clicar em **Add to cart** em "Sauce Labs Backpack" (o botão vira **Remove** e o badge mostra `1`).
3. Abrir o menu lateral e clicar em **Reset App State**.

**Resultado esperado:** carrinho vazio **e** todos os botões voltam a exibir **Add to cart**.

**Resultado obtido:** o badge do carrinho some (carrinho foi limpo), mas o botão do produto continua exibindo **Remove**. A interface fica inconsistente com o estado real do carrinho.

**Impacto:** o usuário acredita que o item ainda está no carrinho.
