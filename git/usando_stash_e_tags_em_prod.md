# 🛡️ Como Atualizar sua Produção para uma Nova Tag de Forma Segura e Reversível Usando Git Stash

Atualizar a produção é sempre um momento crítico. Por mais que a nova versão esteja testada, você nunca sabe se alguém fez alguma "gambiarra urgente" direto no servidor de produção.
Aqui vai um guia **profissional, simples e reversível**, usando apenas `git stash` + `git checkout` + boas práticas de diagnóstico.

---

## ✅ Objetivo:

* Salvar o estado atual da produção **(sem subir para o repositório remoto)**
* Atualizar a produção para uma **tag específica**
* Garantir que, se necessário, você possa **voltar ao exato estado anterior sem perdas**

---

## ✅ Passo 1: Verificar o estado atual da produção

Antes de qualquer coisa, veja se há mudanças locais:

```bash
git status
```

Isso te mostrará:

* Se existem arquivos modificados mas não commitados
* Se há arquivos novos (untracked)
* Se está tudo limpo (working tree clean)

---

## ✅ Passo 2: Fazer um backup local das mudanças (se houver)

Se o `git status` mostrar **qualquer alteração local**, faça um stash:

```bash
git stash push -u -m "Backup produção antes do deploy da tag v0.9.5"
```

📌 Explicando:

* `-u`: Inclui arquivos não rastreados
* `-m`: Nomeia o stash (facilita localizar depois)

---

## ✅ Passo 3: Sincronizar as tags do remoto (caso ainda não tenha feito)

Se a nova tag foi criada recentemente, certifique-se de ter ela localmente:

```bash
git fetch --tags
```

Depois, confirme se a tag existe localmente:

```bash
git tag
```

Procure por `v0.9.5` na lista.

---

## ✅ Passo 4: Atualizar para a nova tag

Agora o momento de checkout para o release:

```bash
git checkout v0.9.5
```

> ✅ Isso vai deixar o código no estado exato da tag, limpo e pronto para rodar em produção.

---

## ✅ Passo 5: Confirmar que tudo está OK

Rode novamente:

```bash
git status
```

Você deve ver:

```
HEAD detached at v0.9.5
nothing to commit, working tree clean
```

Perfeito! Produção agora rodando na nova tag.

---

## ✅ Caso precise voltar: Restaurando o estado anterior

Se o novo release der problema, e você quiser **voltar exatamente ao estado anterior**, basta aplicar o stash:

```bash
git stash list
```

Você verá algo como:

```
stash@{0}: On develop: Backup produção antes do deploy da tag v0.9.5
```

Agora, para restaurar:

```bash
git checkout develop            # Ou a branch que estava antes
git stash apply stash@{0}       # Aplica o stash
```

Se quiser restaurar e limpar da lista de stashes:

```bash
git stash pop stash@{0}
```

---

## ✅ Comandos-Chave Resumo:

| O que fazer               | Comando                                      |
| ------------------------- | -------------------------------------------- |
| Ver estado local          | `git status`                                 |
| Fazer backup local        | `git stash push -u -m "Backup antes da tag"` |
| Sincronizar tags          | `git fetch --tags`                           |
| Listar tags               | `git tag`                                    |
| Atualizar para a tag      | `git checkout vX.Y.Z`                        |
| Listar stashes            | `git stash list`                             |
| Restaurar estado anterior | `git stash apply` ou `git stash pop`         |

---

## ✅ Conclusão:

Esse fluxo é **simples, rápido e seguro**, principalmente em ambientes onde você **não quer criar branchs de backup** nem poluir o repositório remoto.


