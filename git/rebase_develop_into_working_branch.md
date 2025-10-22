# 🔄 Keeping Your Feature Branch Up-to-Date with `develop` Using Rebase

When your feature branch lags behind `develop`, you need to bring in the latest changes. Instead of using `merge`, you can use **rebase**, which gives your branch a clean, linear history.

---

## ✅ Step 1: Update your local repo

Fetch the latest changes:

```bash
git fetch origin
```

---

## ✅ Step 2: Switch to your feature branch

```bash
git checkout feature/new_feature
```

---

## ✅ Step 3: Rebase your branch onto `develop`

Run:

```bash
git rebase origin/develop
```

This does **not** create a merge commit. Instead, Git:

* Takes your feature branch commits
* Temporarily removes them
* Rewinds your branch back to `develop`
* Re-applies your commits *on top* of `develop`

---

## ✅ Step 4: Resolve conflicts (if any)

If there are conflicts, Git will stop and tell you which files are affected.

Resolve them manually, then run:

```bash
git add <conflicted-file>
git rebase --continue
```

If you want to abort and go back to how things were:

```bash
git rebase --abort
```

---

## ✅ Step 5: Push your rebased branch

Since rebase rewrites history, your local branch has different commit IDs. If you already pushed your branch before, you need to **force push**:

```bash
git push --force origin feature/new_feature
```

⚠️ Be careful: force pushing can overwrite history on the remote. Only do this if your branch is *yours alone* (not shared with teammates).

---

## ✅ Step 6: Open your PR

Now your feature branch looks as if it was built on top of the latest `develop` all along. Clean, linear, and easy to follow.

---

# ⚖️ Merge vs. Rebase — Pros & Cons

### 🔀 Merge

✅ **Pros**

* Preserves full history (exactly what happened and when)
* Safe for shared branches (no rewriting history)
* Easier for beginners — fewer risks

❌ **Cons**

* Creates extra merge commits that can clutter history
* History can become harder to follow in busy projects

---

### 📐 Rebase

✅ **Pros**

* Produces a **clean, linear history** (like your feature was always on the latest `develop`)
* Easier to understand with `git log` or `git blame`
* Ideal for polishing history before merging into a shared branch

❌ **Cons**

* Rewrites commit history (dangerous if others are working on the same branch)
* Can be trickier when dealing with conflicts
* Requires `git push --force` if branch was already pushed

---

# 💡 When to Use Each

🔀 **Use Merge when:**

* The branch is shared with multiple developers
* You want to preserve the exact historical record
* You’re less comfortable with Git and want to play safe

📐 **Use Rebase when:**

* You’re the **only person** working on the branch
* You want a **clean, linear history**
* You’re preparing a PR and want to make the reviewer’s life easier
* You’re rebasing local, unpublished commits before pushing

---

# 🚀 My Recommendation

* For **personal feature branches**: Use **rebase** regularly to keep them up-to-date with `develop`. This gives you clean history.
* For **shared feature branches**: Use **merge** to avoid rewriting history others depend on.
* Before merging into `develop`: Both strategies are fine — some teams prefer "merge commits" for traceability, others prefer rebased branches for clarity.

---

👉 Think of it like this:

* **Merge = diary** → preserves *everything* exactly as it happened.
* **Rebase = novel** → rewrites events into a clean, logical sequence.

