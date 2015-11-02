#!/bin/bash
nowdirname=$(dirname $0)


clear_pyc(){
		find $nowdirname -type f -name \*.pyc -exec rm -f {} \;
}

git_check_for_delete(){
		cd $nowdirname
		files=$(git status | grep "deleted:" | awk '{print $3}')
		if [ "$files" != "" ];then
				git rm $files
		fi
}

clear_pyc
git_check_for_delete
