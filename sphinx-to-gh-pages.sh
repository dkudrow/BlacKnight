#!/bin/bash
#
# sphinx-to-gh-pages
#	Build Sphinx docs and push them to Github Pages branch
#

GH_PAGES_SOURCES='doc blacknight'

abort() {
	local cur_branch
	cur_branch = $(git rev-parse --abbrev-ref HEAD)
	if [[ $cur_branch == 'gh-pages' ]]; then
		git reset --hard
		git checkout master
	fi
	exit 1
}

main() {
	git checkout gh-pages || abort
	rm -rf _sources _static
	git checkout master ${GH_PAGES_SOURCES} || abort
	git reset HEAD || abort
	cd doc
	make html || abort
	cd ..
	mv -fv _build/html/* ./
	rm -rf ${GH_PAGES_SOURCES}
	git add -A || abort
	git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" || abort
	git push origin gh-pages || abort
	git checkout master
}

main
