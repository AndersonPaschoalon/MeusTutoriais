# Tutorial: Merge do Branch develop no branch de trabalho

Vou te dar um **passo-a-passo seguro, sem riscos de perder dados**, para trazer `develop` para o seu branch (merge) e inspecionar tudo. Vou assumir que você prefere **merge** (workflow mais conservador) e quer poder **voltar atrás se algo der errado**.

Vou mostrar duas rotas rápidas no início (uma preferida — salvar WIP como commit local — e outra com `stash`) e depois o fluxo principal (fetch/pull develop, merge com revisão, resolver conflitos, commit, push). Em cada passo explico **o que acontece**.

---

## Resumo rápido (comandos principais)

```bash
# (A) Salvar WIP como commit local - RECOMENDADO
git add -A
git commit -m "WIP: salvar progresso antes de mesclar develop" 

git branch backup/minha-branch-before-merge

# Atualizar develop remoto
git fetch origin
git checkout develop
git pull origin develop

# Voltar para sua branch e mesclar (sem commit automático)
git checkout minha-branch
git merge --no-commit --no-ff develop

# Rever mudanças (arquivo a arquivo)
git diff --staged --name-status
git diff --staged -- path/to/file.py

# Se estiver tudo ok
git commit -m "Merge develop into minha-branch (sync)"

# Push
git push origin minha-branch
```

Se preferir usar `stash` (não quiser criar commit WIP), eu dou o fluxo logo a seguir.

---

## Por que criar um **backup** (recomendado)?

* Criar um commit WIP e uma branch de backup garante que **qualquer coisa que aconteça** (merge errado, conflito mal resolvido, reset) você consiga recuperar o estado exato anterior.
* É simples e local — não exige push.

---

## Fluxo completo (passo-a-passo seguro)

> Substitua `minha-branch` pelo nome do seu branch real.

### 1) Verifique seu estado atual

```bash
git status
```

**O que mostra:** arquivos modificados, staged, untracked. Se tiver trabalho não salvo, veja a etapa 2A (commit WIP) ou 2B (stash).

---

### 2A) **Opção RECOMENDADA**: salvar WIP como commit local (mais seguro)

```bash
git add -A
git commit -m "WIP: salvar progresso antes de mesclar develop"
```

**O que faz:** cria um commit com tudo que está alterado. Você pode depois editar / squash / reescrever esse commit se quiser.

Crie uma branch de backup apontando para esse momento:

```bash
git branch backup/minha-branch-before-merge
```

**Por que:** backup local recuperável facilmente.

---

### 2B) (Alternativa) Usar `stash` (se não quiser criar commit)

```bash
git stash push -u -m "WIP before merging develop into minha-branch"
```

**O que faz:** guarda alterações (incluindo arquivos não rastreados com `-u`) numa pilha temporária.
**Nota:** se usar stash, a branch de backup NÃO conterá essas mudanças — o stash as segura.

---

### 3) Atualize o `develop` remoto com segurança

```bash
git fetch origin
git checkout develop
git pull origin develop
```

**O que faz:** `fetch` baixa referências; `pull` atualiza sua branch `develop` com o que está no remote.

---

### 4) Volte para sua branch de trabalho

```bash
git checkout minha-branch
```

---

### 5) Faça o merge **sem** commitar automaticamente (revisável)

```bash
git merge --no-commit --no-ff develop
```

**O que faz:** aplica o conteúdo do `develop` no seu branch, atualizando o índice, **mas pára antes de criar o commit de merge**.

* Se houver **conflitos**, o merge vai parar e mostrar os arquivos com conflito.
* Se **não houver conflitos**, todas as mudanças estarão staged (index) aguardando seu review.

> Vantagem: você pode ver tudo que será commitado e abortar se algo errado (`git merge --abort`) antes que o merge seja finalizado.

---

### 6) Inspecione as alterações arquivo por arquivo

#### Lista de arquivos que serão alterados / staged:

```bash
git diff --staged --name-status
```

* Mostra para cada arquivo: `A` (added), `M` (modified), `D` (deleted).

#### Ver diff completo (conteúdo) do que foi staged:

```bash
git diff --staged
```

#### Ver apenas um arquivo específico:

```bash
git diff --staged -- path/to/file.py
```

#### Ver diferenças entre sua branch pré-merge e develop (antes do merge, alternativa):

```bash
git diff --name-status develop..minha-branch
# ou para ver o que o develop tem de novo sobre sua branch
git diff --name-status minha-branch..develop
```

**Explanação:** `--staged` mostra as diferenças entre índice (resultado do merge) e o HEAD anterior ao merge — é o conjunto que será gravado no commit de merge.

---

### 7) Se você não gostar do que vê — **abortar** o merge

```bash
git merge --abort
```

**O que faz:** cancela o merge em andamento e restaura seu branch ao estado anterior ao `git merge`.

Se você havia feito commit WIP antes, esse commit continua seguro na sua branch/backup.

---

### 8) Se tudo estiver ok — finalize o merge (commit)

```bash
git commit -m "Merge develop into minha-branch (sync with develop)"
```

**O que faz:** cria o commit de merge contendo as mudanças integradas.

---

### 9) Teste localmente e rode seus testes / app

Execute seus testes e verifique se tudo roda bem. Só depois disso faça push.

---

### 10) Push do seu branch com as mudanças

```bash
git push origin minha-branch
```

---

## E se eu usei `stash` no passo 2B?

Depois de terminar o merge e commit (ou se abortou e quer reaplicar o WIP):

* Reaplicar o stash:

```bash
git stash list            # ver os stashes
git stash pop             # reaplica o último e remove da lista
# ou
git stash apply stash@{0} # reaplica sem remover
```

* Atenção: `stash pop` pode gerar conflitos se as mudanças do stash e as do merge mexeram nas mesmas linhas — resolva igual conflito normal.

---

## Como voltar ao estado **exato** anterior, se algo der errado?

Se você fez o **backup branch** no passo 2A:

* Voltar para o backup exatamente como estava:

```bash
git checkout backup/minha-branch-before-merge
# ou sobrescrever sua branch atual:
git checkout minha-branch
git reset --hard backup/minha-branch-before-merge
```

> `reset --hard` **sobrescreve** seu working tree para igualar o backup — use com cuidado, mas é exatamente o que você quer se quiser desfazer o merge por completo.

Se você só usou `stash` e abortou o merge, basta:

```bash
git stash pop
```

(ou `apply` e resolver conflitos)

---

## Resumo de comandos (copy-paste)

```bash
# 0. Veja em que branch está
git branch --show-current

# 1. Salvar WIP (RECOMENDADO)
git add -A
git commit -m "WIP: salvar progresso antes de mesclar develop"
git branch backup/minha-branch-before-merge

# 2. Atualizar develop
git fetch origin
git checkout develop
git pull origin develop

# 3. Voltar para sua branch e iniciar merge revisável
git checkout minha-branch
git merge --no-commit --no-ff develop

# 4. Inspecionar mudanças (arquivo-a-arquivo)
git diff --staged --name-status
git diff --staged -- path/to/file.py

# 5a. Se não gostar: abortar merge
git merge --abort

# 5b. Se tudo certo: commit e push
git commit -m "Merge develop into minha-branch (sync)"
git push origin minha-branch

# -> Recuperar do backup se necessário
git reset --hard backup/minha-branch-before-merge
```

---

## Dicas finais

* **Nunca** faça `push --force` do branch compartilhado sem avisar (merge não necessita disso).
* Se você trabalha sozinho na branch, `rebase` também é opção, mas você preferiu **merge** — ótima escolha para segurança.
* Usar um **commit WIP** é geralmente a maneira mais simples para garantir backup local sem mexer no remoto. Você pode depois **squash** ou reorganizar os commits se quiser antes de abrir PR.

---

Se quiser, eu posso:

* Gerar um **script** que faz backup + merge interativo (com prompts), ou
* Acompanhar passo-a-passo enquanto você executa (tu me cola os outputs e eu te oriento).

Quer que eu gere o script seguro (bash) para você rodar?
