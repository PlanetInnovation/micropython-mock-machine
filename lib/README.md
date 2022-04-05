# Lib

If your library is dependent on _other_ libraries, `lib` is where these dependencies should be located.

Typically a _git submodule_ will be used to manage a _reference_ to another repository in the `lib` folder.

## git submodule example

To add [micropython-max7219](https://github.com/mattytrentini/micropython-max7219) as a git submodule to the `lib` folder:

```bash
> cd lib
> git submodule add https://github.com/mattytrentini/micropython-max7219
Cloning into 'micropython-max7219'...
remote: Counting objects: 11, done.
remote: Compressing objects: 100% (10/10), done.
remote: Total 11 (delta 0), reused 11 (delta 0)
Unpacking objects: 100% (11/11), done.
Checking connectivity... done.
```

There will now be a `micropython-max7219` folder inside `lib` containing the latest code from the `micropython-max7219` repository.

Look at the output of `git status`:

```bash
> git status
On branch master
Your branch is up-to-date with 'origin/master'.

Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)

	new file:   .gitmodules
	new file:   micropython-max7219
```

These are explained in the references below but both files need to be committed for the submodule to operate correctly.

### References

* [Git Tools - Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
* [Git submodules](https://www.atlassian.com/git/tutorials/git-submodule)
* [Working with submodules](https://github.blog/2016-02-01-working-with-submodules/)
