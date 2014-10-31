branch=`git rev-parse --abbrev-ref HEAD`
echo "pushing to "$branch
git push origin $branch

